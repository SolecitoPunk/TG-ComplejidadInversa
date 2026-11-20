"""
Bloque 3: línea base (U = -ln P, flujo medido) frente a V_Bohm y V completo.

    python b3_linea_base.py

Configuración fija (decidida en el bloque 2): cierre 'ninguna', corriente con punto medio,
tiempo normalizado al periodo (dt = 1/T_refinado). Estado principal Barrat; Onnela como sensibilidad.

Campos sobre la malla (máscara P > 5 % del máximo):
  U     = -ln P
  V_B   = bohm1 = (1/4)[lap P/P - (1/2)|grad P|^2/P^2]     (por unidad de lambda; su forma no depende de lambda)
  V(l)  = l * bohm1 - |u|^2/2                              (l = lambda tau^2, único parámetro libre)

Mínimos y barreras: persistencia 0-dimensional de los conjuntos de subnivel (unión-búsqueda, 8 vecinos,
solo dentro de la máscara). La persistencia de un mínimo es la altura del punto de silla por el que su
cuenca se une a una cuenca más profunda, menos su valor: es la barrera del mínimo. Se reporta relativa
al rango del campo en la máscara. Se descartan los mínimos que tocan el borde de la máscara.

Estabilidad: se toman los K_TOP mínimos más persistentes de la referencia (h = 0.35, refine 10) y se
cuenta qué fracción tiene un mínimo de los K_TOP de la configuración perturbada a menos de D_MATCH.

Circulación (sin kernel): área con signo de cada lazo cerrado, A_i = (1/2) sum (x dy - y dx).
Con kernel, sobre los lazos de mayor |A_i|:
  Gamma = sum u . dl                (u evaluado en los puntos medios del lazo)
  Phi   = sum J . dl / L            (análogo al de Wang: flujo integrado / longitud del lazo)
Cada uno con u o J de todos los nodos ('propio') y excluyendo al nodo del lazo ('loo'). La versión
'propio' está sesgada hacia valores positivos: la velocidad del propio nodo se alinea con dl.

Salida: resultados/b3_*.csv. Predicciones en README_bloque3.md.
"""
import os
import time

import numpy as np
import pandas as pd

from campos import malla, muestras, densidad_kde, corriente_kde, campos_derivados, div_relativa
from phasik import cargar_series, construir_W, refinar_tiempo, trayectorias

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
CLUSTERINGS = ("barrat", "onnela")
H_REF, REF_REF = 0.35, 10
PERTURBACIONES = [("h", 0.25), ("h", 0.5), ("refine", 5), ("refine", 20)]
LAMBDAS = (1.0, 0.1, 0.01, 0.003, 0.001)
N_GRID = 60
MASK_FRAC = 0.05
K_TOP = 5
D_MATCH = 0.35       # distancia de emparejamiento = h de referencia (declarado)
PERS_MIN = 0.05      # persistencia relativa mínima para contar un mínimo como "relevante"
N_LAZOS = 5


def _imprimir(df, nombre):
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, nombre), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 40):
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


# ============================================================
# Datos y campos
# ============================================================
_CACHE_W = {}


def preparar(clustering, refine):
    if "W0" not in _CACHE_W:
        nombres, X = cargar_series(cierre="ninguna")
        _CACHE_W["W0"], _CACHE_W["nodos"], _ = construir_W(nombres, X)
    r, _ = trayectorias(refinar_tiempo(_CACHE_W["W0"], refine), clustering)
    return r, _CACHE_W["nodos"]


def campos_en_malla(r, G, h):
    T = r.shape[0]
    A, B, Vel = muestras(r, 1.0 / T, "medio", cerrado=True)
    P, gP, lP = densidad_kde(G, A, h)
    J, gJ = corriente_kde(G, B, Vel, h)
    return campos_derivados(P, gP, lP, J, gJ)


def campos_escalares(F, shape):
    out = {"U": F["U"].reshape(shape), "V_B": F["bohm1"].reshape(shape)}
    for lam in LAMBDAS:
        out[f"V(l={lam:g})"] = (lam * F["bohm1"] + F["flujo"]).reshape(shape)
    return out


# ============================================================
# Persistencia de mínimos (unión-búsqueda)
# ============================================================
_VEC8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def minimos_persistentes(Z, mask):
    """Devuelve una lista de dicts (i, j, valor, pers_rel, borde) con un elemento por mínimo local
    dentro de la máscara. pers_rel = persistencia / rango(Z en la máscara); la cuenca más profunda
    de cada componente conexa recibe pers_rel = 1."""
    nx_, ny_ = Z.shape
    zf = Z.ravel()
    valid = mask.ravel() & np.isfinite(zf)
    orden = np.flatnonzero(valid)
    orden = orden[np.argsort(zf[orden], kind="stable")]
    rango = np.ptp(zf[valid]) if valid.any() else 1.0
    padre = -np.ones(zf.size, dtype=np.int64)
    raiz_min = np.zeros(zf.size, dtype=np.int64)
    pers = {}

    def find(p):
        while padre[p] != p:
            padre[p] = padre[padre[p]]
            p = padre[p]
        return p

    for p in orden:
        i, j = divmod(int(p), ny_)
        padre[p] = p
        raiz_min[p] = p
        raices = set()
        for di, dj in _VEC8:
            a, b = i + di, j + dj
            if 0 <= a < nx_ and 0 <= b < ny_:
                q = a * ny_ + b
                if padre[q] >= 0:
                    raices.add(find(q))
        if not raices:
            continue                                   # p es un mínimo nuevo
        raices = sorted(raices, key=lambda rt: zf[raiz_min[rt]])
        mayor = raices[0]
        for rt in raices[1:]:                          # regla del más antiguo: muere la cuenca menos profunda
            pers[int(raiz_min[rt])] = (zf[p] - zf[raiz_min[rt]]) / rango
            padre[rt] = mayor
        padre[p] = mayor
    for p in orden:                                    # cuencas que nunca se unieron a otra más profunda
        if padre[p] == p:
            pers.setdefault(int(raiz_min[p]), 1.0)
    salida = []
    m2 = mask & np.isfinite(Z)
    for p, pr in pers.items():
        i, j = divmod(p, ny_)
        borde = any(not (0 <= i + di < nx_ and 0 <= j + dj < ny_) or not m2[i + di, j + dj] for di, dj in _VEC8)
        salida.append(dict(i=i, j=j, valor=zf[p], pers_rel=pr, borde=borde))
    return salida


def top_minimos(mins, X, Y, k=K_TOP):
    buenos = sorted((m for m in mins if not m["borde"]), key=lambda m: -m["pers_rel"])[:k]
    return np.array([[X[m["i"], m["j"]], Y[m["i"], m["j"]]] for m in buenos]).reshape(-1, 2), \
        np.array([m["pers_rel"] for m in buenos])


def emparejar(ref_pos, ref_pers, pos, pers):
    """Fracción de mínimos de referencia con pareja a < D_MATCH, y mediana de |Δpers|/pers en los emparejados."""
    if len(ref_pos) == 0:
        return np.nan, np.nan
    if len(pos) == 0:
        return 0.0, np.nan
    d = np.linalg.norm(ref_pos[:, None, :] - pos[None, :, :], axis=-1)
    j = d.argmin(1)
    ok = d[np.arange(len(ref_pos)), j] < D_MATCH
    dp = np.abs(pers[j[ok]] - ref_pers[ok]) / ref_pers[ok] if ok.any() else np.array([np.nan])
    return ok.mean(), float(np.median(dp))


# ============================================================
# Circulación
# ============================================================
def areas_con_signo(r):
    r1 = np.roll(r, -1, axis=0)
    return 0.5 * (r[..., 0] * r1[..., 1] - r1[..., 0] * r[..., 1]).sum(0)      # (N,)


def integrales_lazo(r, i, h):
    """Gamma y Phi sobre el lazo del nodo i, con todos los nodos y excluyendo al nodo i."""
    T, N, _ = r.shape
    A, B, Vel = muestras(r, 1.0 / T, "medio", cerrado=True)
    nodo = np.tile(np.arange(N), T)                     # índice de nodo de cada muestra (orden t, n)
    ri = r[:, i, :]
    r1 = np.roll(ri, -1, axis=0)
    m, dl = 0.5 * (ri + r1), r1 - ri
    L = np.linalg.norm(dl, axis=1).sum()
    out = {}
    for etiqueta, sel in (("propio", np.ones_like(nodo, bool)), ("loo", nodo != i)):
        P, _, _ = densidad_kde(m, A[sel], h)
        J, _ = corriente_kde(m, B[sel], Vel[sel], h)
        # normalización: P y J se promedian sobre el mismo número de muestras, así u = J/P es correcto
        with np.errstate(divide="ignore", invalid="ignore"):
            u = J / P[:, None]
        out[f"Gamma_{etiqueta}"] = float(np.nansum((u * dl).sum(1)))
        out[f"Phi_{etiqueta}"] = float((J * dl).sum() / L)
    out["L"] = L
    return out


# ============================================================
# Programa principal
# ============================================================
def main():
    filas_cfg, filas_est, filas_lam, filas_circ = [], [], [], []
    for clus in CLUSTERINGS:
        r_ref, nodos = preparar(clus, REF_REF)
        S = r_ref.reshape(-1, 2)
        lo, hi = S.min(0) - 1.0, S.max(0) + 1.0
        X, Y, G = malla(lo, hi, N_GRID)                 # malla fija por clustering (extensión de refine 10)
        estaticos = r_ref[0, np.linalg.norm(np.diff(r_ref, axis=0), axis=-1).sum(0) < 1e-9]

        configs = [("ref", None)] + PERTURBACIONES
        tops = {}
        for tipo, val in configs:
            t0 = time.time()
            h = val if tipo == "h" else H_REF
            refine = val if tipo == "refine" else REF_REF
            r = r_ref if refine == REF_REF else preparar(clus, refine)[0]
            F = campos_en_malla(r, G, h)
            mask = F["P"] > MASK_FRAC * F["P"].max()
            Jn = np.linalg.norm(F["J"], axis=1)
            fila = dict(clustering=clus, config=f"{tipo}={val}" if val is not None else "ref", h=h, refine=refine,
                        subpaso_max_sobre_h=np.linalg.norm(np.diff(r, axis=0), axis=-1).max() / h,
                        div_rel=div_relativa(F, mask, h),
                        masa_P_en_mascara=F["P"][mask].sum() / F["P"].sum(),
                        masa_J_en_mascara=Jn[mask].sum() / Jn.sum(),
                        rango_flujo_sobre_bohm_l1=np.ptp(F["flujo"][mask]) / np.ptp(F["bohm1"][mask]))
            Z = campos_escalares(F, X.shape)
            m2 = mask.reshape(X.shape)
            tops[(tipo, val)] = {}
            for nombre, Zc in Z.items():
                mins = minimos_persistentes(Zc, m2)
                pos, pr = top_minimos(mins, X, Y)
                tops[(tipo, val)][nombre] = (pos, pr)
                n_rel = sum(1 for mm in mins if not mm["borde"] and mm["pers_rel"] >= PERS_MIN)
                fila[f"nmin_{nombre}"] = sum(1 for mm in mins if not mm["borde"])
                fila[f"nrel_{nombre}"] = n_rel
                if nombre in ("U", "V_B"):
                    cerca = (np.linalg.norm(pos[:, None] - estaticos[None], axis=-1).min(1) < D_MATCH
                             if len(pos) and len(estaticos) else np.array([]))
                    fila[f"top_cerca_estatico_{nombre}"] = cerca.mean() if len(cerca) else np.nan
            filas_cfg.append(fila)
            print(f"  {clus} {fila['config']}: {time.time() - t0:.1f} s")

        ref = tops[("ref", None)]
        for tipo, val in PERTURBACIONES:
            for nombre in ref:
                mr, dp = emparejar(*ref[nombre], *tops[(tipo, val)][nombre])
                filas_est.append(dict(clustering=clus, perturbacion=f"{tipo}={val}", campo=nombre,
                                      frac_emparejados=mr, dpers_rel_mediana=dp))
        for nombre in ref:
            if nombre.startswith("V(l="):
                a, _ = emparejar(*ref[nombre], *ref["V_B"])
                b, _ = emparejar(*ref[nombre], *ref["U"])
                filas_lam.append(dict(clustering=clus, campo=nombre, frac_en_top_V_B=a, frac_en_top_U=b))
        a, _ = emparejar(*ref["V_B"], *ref["U"])
        filas_lam.append(dict(clustering=clus, campo="V_B", frac_en_top_V_B=1.0, frac_en_top_U=a))

        Ai = areas_con_signo(r_ref)
        mov = np.linalg.norm(np.diff(r_ref, axis=0), axis=-1).sum(0) > 1e-9
        filas_circ.append(dict(clustering=clus, nodo="TOTAL", A=Ai[mov].sum(), absA=np.abs(Ai[mov]).sum(),
                               coherencia=abs(Ai[mov].sum()) / np.abs(Ai[mov]).sum()))
        for i in np.argsort(-np.abs(Ai))[:N_LAZOS]:
            d = integrales_lazo(r_ref, i, H_REF)
            filas_circ.append(dict(clustering=clus, nodo=nodos[i], A=Ai[i], absA=abs(Ai[i]), **d))

    print("\n=== Configuraciones ===")
    _imprimir(pd.DataFrame(filas_cfg), "b3_configuraciones.csv")
    print("\n=== Estabilidad de los mínimos más persistentes (frente a h = 0.35, refine 10) ===")
    est = pd.DataFrame(filas_est)
    _imprimir(est, "b3_estabilidad.csv")
    print("\nResumen: fracción emparejada media por campo")
    with pd.option_context("display.width", 200):
        print(est.pivot_table(index="campo", columns="clustering", values="frac_emparejados", aggfunc="mean")
              .to_string(float_format=lambda v: f"{v:.2f}"))
    print("\n=== Dependencia en lambda: ¿los mínimos de V(l) son los de V_B o los de U? ===")
    _imprimir(pd.DataFrame(filas_lam), "b3_lambda.csv")
    print("\n=== Circulación ===")
    _imprimir(pd.DataFrame(filas_circ), "b3_circulacion.csv")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"[b3] {time.time() - t0:.1f} s")
