"""
Bloque 2: diagnóstico de discontinuidades y cierre del ciclo en Phasik.

    python b2_diagnostico.py

Partes:
  A. Hechos de los datos (grado constante, series duplicadas, pesos mínimos).
  B. Tabla de saltos en el plano (log(1+s), C) con TIME_REFINE = 1 y causa probable de cada uno.
     Normalización doble: por el paso mediano GLOBAL (todos los nodos que se mueven)
     y por el paso mediano PROPIO del nodo (métrica del pipeline original).
  C. Efecto de clustering (onnela/barrat), opción de cierre (ninguna/droplast/lineal/subconjunto)
     y TIME_REFINE (1/10) en el índice de cierre y en la divergencia relativa de J
     (esquemas hacia adelante y de punto medio).
Las predicciones están en README_bloque2.md. Salida: resultados/b2_*.csv
"""
import os
import time

import numpy as np
import pandas as pd

from campos import malla, muestras, densidad_kde, corriente_kde, campos_derivados, div_relativa
from phasik import cargar_series, construir_W, refinar_tiempo, trayectorias, CIERRES

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
H = 0.35
N_GRID = 50
MASK_FRAC = 0.05
UMBRAL_DW = 0.3        # |Δw| en un paso considerado "salto real de pesos" (declarado, no ajustado)
UMBRAL_AMP = 1.0       # amplificación raíz cúbica: sum|Δ w^(1/3)| / sum|Δw| (vale 1/3 si w ~ 1)
UMBRAL_BARRAT = 0.3    # |ΔC_barrat| / |ΔC_onnela| por debajo de esto: el salto es propio de Onnela
UMBRAL_BRECHA = 2.0    # 'subconjunto': conserva nodos con brecha de cierre <= 2 pasos medianos globales


def _imprimir(df, nombre):
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, nombre), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.max_colwidth", 40):
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


def pasos(r):
    """|r(t+1) - r(t)| con el segmento de cierre T-1 -> 0 en la última fila. (T, N)"""
    return np.linalg.norm(np.roll(r, -1, axis=0) - r, axis=-1)


# ============================================================
# A. Hechos de los datos
# ============================================================
def parte_A():
    print("\n=== A. Hechos de los datos ===")
    nombres, X = cargar_series()
    W, nodos, tem = construir_W(nombres, X)
    _, k = trayectorias(W, "onnela")
    print(f"Nodos {len(nodos)}, instantes {X.shape[0]}, series {X.shape[1]}, aristas temporales casadas {len(tem)}")
    print(f"Máximo por serie == 1 en {int(np.sum(np.isclose(X.max(0), 1)))} de {X.shape[1]}; "
          f"mínimo de los mínimos = {X.min():.3g}; series con mínimo < 1e-3: {int(np.sum(X.min(0) < 1e-3))}")
    print(f"Pasos (t, nodo) con cambio de grado k: {int(np.sum(np.diff(k, axis=0) != 0))}")
    dup = {}
    for j, n in enumerate(nombres):
        dup.setdefault(X[:, j].round(12).tobytes(), []).append(n)
    print("Series idénticas:", [g for g in dup.values() if len(g) > 1])
    d = np.linalg.norm(np.diff(X, axis=0), axis=1)
    print(f"Espacio de aristas: paso mediano {np.median(d):.3f}, cierre ||x(101)-x(0)|| = "
          f"{np.linalg.norm(X[-1] - X[0]):.3f}; mayores pasos en t = {np.argsort(-d)[:5].tolist()}")


# ============================================================
# B. Tabla de saltos
# ============================================================
def parte_B(n_top=12):
    print("\n=== B. Saltos en el plano (TIME_REFINE = 1, cierre 'ninguna') ===")
    nombres, X = cargar_series()
    W, nodos, tem = construir_W(nombres, X)
    T = X.shape[0]
    r_on, k = trayectorias(W, "onnela")
    r_ba, _ = trayectorias(W, "barrat")
    st_on, st_ba = pasos(r_on), pasos(r_ba)
    mov = st_on.sum(0) > 1e-9
    mov_ba = st_ba.sum(0) > 1e-9
    med_g_on = np.median(st_on[:, mov])
    med_g_ba = np.median(st_ba[:, mov_ba])            # cada clustering con sus propios nodos móviles
    med_prop = np.median(st_on, axis=0)
    med_prop = np.where(med_prop > 0, med_prop, np.nan)   # paso mediano 0 -> NaN (antes daba inf)
    print(f"Nodos que se mueven: {mov.sum()} de {len(nodos)}; paso mediano global (Onnela) = {med_g_on:.4g}")

    # aristas temporales relevantes para el nodo i: incidentes (afectan s y C)
    # y entre dos vecinos de i (afectan solo C, vía triángulos). Se guarda (etiqueta, columna).
    Adj = W[0] > 0
    inc = {i: [] for i in range(len(nodos))}
    for a, b, c in tem:
        for i in range(len(nodos)):
            if i in (a, b):
                inc[i].append((f"{nodos[a]}-{nodos[b]}", c))
            elif Adj[i, a] and Adj[i, b]:
                inc[i].append((f"[{nodos[a]}-{nodos[b]}]", c))
    Xc = np.vstack([X, X[:1]])                      # para el segmento de cierre t = T-1 -> 0

    cand = [(st_on[t, i] / med_g_on, t, i) for t in range(T) for i in np.where(mov)[0]]
    filas = []
    for rel, t, i in sorted(cand, reverse=True)[:n_top]:
        t1 = (t + 1) % T
        dx = abs(r_on[t1, i, 0] - r_on[t, i, 0])
        dC_on = abs(r_on[t1, i, 1] - r_on[t, i, 1])
        dC_ba = abs(r_ba[t1, i, 1] - r_ba[t, i, 1])
        dws = [(abs(Xc[t + 1, c] - Xc[t, c]), j, c) for j, c in inc[i]]
        sum_dw = sum(v for v, _, _ in dws)
        sum_dcb = sum(abs(np.cbrt(Xc[t + 1, c]) - np.cbrt(Xc[t, c])) for _, _, c in dws)
        amp = sum_dcb / sum_dw if sum_dw > 0 else np.nan
        dw_max, jm, cm = max(dws) if dws else (0.0, None, None)   # jm: etiqueta; [A-B] = arista entre vecinos
        dk = int(k[t1, i] - k[t, i])
        ratio_ba = dC_ba / dC_on if dC_on > 0 else np.nan
        if dk != 0:
            causa = "cambio de grado"
        elif dw_max >= UMBRAL_DW:
            causa = "salto real de pesos"
        elif amp > UMBRAL_AMP and ratio_ba < UMBRAL_BARRAT:
            causa = "amplificación raíz cúbica (Onnela)"
        else:
            causa = "otra / no clasificada"
        filas.append(dict(
            nodo=nodos[i], t=f"{t}->{t1}", paso_global=rel, paso_propio=st_on[t, i] / med_prop[i],
            paso_global_barrat=st_ba[t, i] / med_g_ba,
            dx_std=dx, dC_onnela_std=dC_on, dC_barrat_std=dC_ba, dk=dk,
            arista_max_dw=jm if jm is not None else "",
            dw_max=dw_max, w_antes=Xc[t, cm] if cm is not None else np.nan,
            w_despues=Xc[t + 1, cm] if cm is not None else np.nan,
            amp_cbrt=amp, causa=causa))
    _imprimir(pd.DataFrame(filas), "b2_saltos.csv")

    print("\nMétrica del pipeline original frente a la global (top 6 por paso propio):")
    big_p = st_on.max(0) / med_prop
    orden = [i for i in np.argsort(-np.nan_to_num(big_p, nan=-1)) if mov[i]][:6]
    comp = pd.DataFrame([dict(nodo=nodos[i], max_paso_propio=big_p[i], max_paso_global=st_on[:, i].max() / med_g_on,
                              paso_mediano_propio_sobre_global=med_prop[i] / med_g_on,
                              t_max=int(np.argmax(st_on[:, i]))) for i in orden])
    _imprimir(comp, "b2_metrica_propia_vs_global.csv")


# ============================================================
# C. Opciones de cierre, clustering y refinamiento
# ============================================================
def _nodos_subconjunto():
    nombres, X = cargar_series()
    W, _, _ = construir_W(nombres, X)
    r, _ = trayectorias(W, "onnela")
    st = pasos(r)
    mov = st.sum(0) > 1e-9
    brecha = st[-1] / np.median(st[:, mov])
    return ~mov | (brecha <= UMBRAL_BRECHA)


def parte_C(refines=(1, 10)):
    print("\n=== C. Cierre y divergencia ===")
    keep_sub = _nodos_subconjunto()
    filas = []
    for clus in ("onnela", "barrat"):
        for cierre in CIERRES + ("subconjunto",):
            nombres, X = cargar_series(cierre="ninguna" if cierre == "subconjunto" else cierre)
            W0, nodos, _ = construir_W(nombres, X)
            for f in refines:
                t0 = time.time()
                r, _ = trayectorias(refinar_tiempo(W0, f), clus)
                if cierre == "subconjunto":
                    r = r[:, keep_sub]
                st = pasos(r)
                mov = st.sum(0) > 1e-9
                med = np.median(st[:, mov])
                prop = np.median(st[:, mov], axis=0)
                cierre_nodo = st[-1, mov] / np.where(prop > 0, prop, np.nan)
                fila = dict(clustering=clus, cierre=cierre, refine=f, nodos=r.shape[1], moviles=int(mov.sum()),
                            indice_cierre=st[-1, mov].mean() / med,
                            frac_nodos_brecha_gt3=float(np.nanmean(cierre_nodo > 3)),
                            max_paso_global=st[:, mov].max() / med)
                Tn = r.shape[0]
                S = r.reshape(-1, 2)
                lo, hi = S.min(0) - 1.0, S.max(0) + 1.0
                _, _, G = malla(lo, hi, N_GRID)
                A, _, _ = muestras(r, 1.0 / Tn, "adelante", cerrado=True)
                P, gP, lP = densidad_kde(G, A, H)
                mask = P > MASK_FRAC * P.max()
                for esq in ("adelante", "medio"):
                    _, B, Vel = muestras(r, 1.0 / Tn, esq, cerrado=True)
                    J, gJ = corriente_kde(G, B, Vel, H)
                    fila[f"div_rel_{esq}"] = div_relativa(campos_derivados(P, gP, lP, J, gJ), mask, H)
                filas.append(fila)
                print(f"  {clus} {cierre} refine={f}: {time.time() - t0:.1f} s")
    _imprimir(pd.DataFrame(filas), "b2_cierre_divergencia.csv")


if __name__ == "__main__":
    t0 = time.time()
    parte_A()
    parte_B()
    parte_C()
    print(f"[b2] {time.time() - t0:.1f} s")
