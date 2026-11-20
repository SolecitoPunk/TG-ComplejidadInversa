"""
Bloque 7: nulo por nodos y contraste CONFIRMATORIO de la señal en u (bloque 5, post hoc).

    python b7_nulo_nodos.py 50       # vista previa (~10 min)
    python b7_nulo_nodos.py          # 400 réplicas, h = 0.25, 0.35, 0.5 (~1 h)

Motivo: las series de arista se explican casi por completo como producto de actividades de nodo,
    log w_e(t) = c_e + a_u(t) + a_v(t) + residuo,   R^2 = 0.948
(con las series asignadas al azar a las aristas, R^2 ~ 0.63). Las aristas que comparten un nodo
están correlacionadas por construcción, y los nulos por arista del bloque 5 rompen esa correlación.

Nulo por nodos:
  1. a(t) = lstsq(M, L(t) - media_t L), con M la incidencia arista-nodo (34 x 22, rango 21; la
     solución de norma mínima fija la ambigüedad de la componente bipartita BUB2/CDC15/LTE1/TEM1).
  2. Modelo:  w_e(t) = exp(c_e + a_u(t) + a_v(t)), dividido por su máximo (como el CSV).
  3. Réplica: desfase circular independiente de cada a_i(t); se reconstruyen las aristas.
  Conserva la dinámica de cada nodo y la correlación entre aristas con nodo común; destruye la
  sincronía entre nodos. El observado del contraste es el MODELO (sin residuo), para comparar
  lo mismo con lo mismo. También se reportan los estadísticos de los datos reales.

Contrastes declarados ANTES de ejecutar (Barrat, refine 10, malla 40):
  confirmatoria: u_max_mascara y rango_flujo, con h = 0.25, 0.35 y 0.5 (6 contrastes, Holm)
  control:       rango_bohm1 con los mismos h (3 contrastes, Holm)
  secundaria:    A_total, coherencia, omega_media_P con h = 0.35 (3 contrastes, Holm)
Con 400 réplicas, p mínimo = 2/401 y p_holm mínimo de la confirmatoria = 0.03.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

from campos import malla
from comunes import estadisticos_globales
from phasik import cargar_series, construir_W, refinar_tiempo, trayectorias
from b5_nulos import valor_p, holm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
SEED = 2026
HS = (0.25, 0.35, 0.5)
H_SEC = 0.35
REFINE = 10
CLUS = "barrat"
N_GRID = 40
CONFIRMATORIA = ["u_max_mascara", "rango_flujo"]
CONTROL = ["rango_bohm1"]
SECUNDARIA = ["A_total", "coherencia", "omega_media_P"]


def modelo_nodos(nombres, X):
    aristas = [tuple(n.split("-")) for n in nombres]
    nodos = sorted({v for e in aristas for v in e})
    idx = {v: i for i, v in enumerate(nodos)}
    M = np.zeros((len(aristas), len(nodos)))
    for k, (u, v) in enumerate(aristas):
        M[k, idx[u]] = M[k, idx[v]] = 1.0
    L = np.log(X)
    c = L.mean(0)
    a = np.linalg.lstsq(M, (L - c).T, rcond=None)[0].T          # (T, n_nodos), norma mínima
    pred = c + a @ M.T
    r2 = 1 - ((L - pred) ** 2).sum() / ((L - c) ** 2).sum()
    return M, c, a, r2, nodos, np.linalg.matrix_rank(M)


def reconstruir(M, c, a):
    Xm = np.exp(c + a @ M.T)
    return Xm / Xm.max(0)


def estado(X, nombres):
    W, _, _ = construir_W(nombres, X)
    r, _ = trayectorias(refinar_tiempo(W, REFINE), CLUS)
    return r


def stats_multi_h(r, G):
    out = {}
    for h in HS:
        st = estadisticos_globales(r, G, h, con_kde=True)
        for k, v in st.items():
            out[f"{k}@h={h}"] = v
    return out


def main(n_rep=400):
    t0 = time.time()
    nombres, X = cargar_series(cierre="ninguna")
    M, c, a, r2, nodos, rango = modelo_nodos(nombres, X)
    Xm = reconstruir(M, c, a)
    print(f"Modelo de nodos: {len(nodos)} nodos, rango de la incidencia {rango}, R^2 = {r2:.4f}")
    print(f"Error del modelo frente al CSV: mediana |dw| = {np.median(np.abs(Xm - X)):.3g}, "
          f"máximo = {np.abs(Xm - X).max():.3g}")

    r_real = estado(X, nombres)
    S = r_real.reshape(-1, 2)
    _, _, G = malla(S.min(0) - 1.5, S.max(0) + 1.5, N_GRID)
    obs_real = stats_multi_h(r_real, G)
    obs_mod = stats_multi_h(estado(Xm, nombres), G)

    rng = np.random.default_rng(SEED)
    T = X.shape[0]
    reps = []
    for rep in range(n_rep):
        sh = rng.integers(T, size=a.shape[1])
        a_n = np.stack([np.roll(a[:, i], sh[i]) for i in range(a.shape[1])], axis=1)
        reps.append(stats_multi_h(estado(reconstruir(M, c, a_n), nombres), G))
        if (rep + 1) % 50 == 0:
            print(f"  {rep + 1} réplicas, {time.time() - t0:.0f} s")
    df = pd.DataFrame(reps)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "b7_replicas.csv"), index=False)

    familias = {"confirmatoria": [f"{k}@h={h}" for k in CONFIRMATORIA for h in HS],
                "control": [f"{k}@h={h}" for k in CONTROL for h in HS],
                "secundaria": [f"{k}@h={H_SEC}" for k in SECUNDARIA]}
    filas = []
    for fam, claves in familias.items():
        sub = []
        for k in claves:
            v = df[k].to_numpy()
            sub.append(dict(familia=fam, estadistico=k, real=obs_real[k], modelo=obs_mod[k],
                            nulo_mediana=np.nanmedian(v), nulo_p2_5=np.nanpercentile(v, 2.5),
                            nulo_p97_5=np.nanpercentile(v, 97.5),
                            z=(obs_mod[k] - np.nanmean(v)) / np.nanstd(v), p=valor_p(obs_mod[k], v)))
        for f, q in zip(sub, holm([s["p"] for s in sub])):
            f["p_holm"] = q
        filas += sub
    res = pd.DataFrame(filas)
    res.to_csv(os.path.join(OUT, "b7_resumen.csv"), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(f"\n=== Nulo por nodos ({n_rep} réplicas). p y z usan el observado del MODELO ===")
        print(res.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print(f"[b7] {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
