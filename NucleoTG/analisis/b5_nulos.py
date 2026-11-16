"""
Bloque 5: modelos nulos para la circulación, la vorticidad y el peso del flujo.

    python b5_nulos.py              # 200 réplicas por nulo (estimado: 15-30 min en total)
    python b5_nulos.py 50           # prueba rápida con 50 réplicas

Nulos (cada uno conserva cada serie temporal completa):
  desfase    : desfase circular aleatorio por GRUPO de series idénticas (27 grupos; los 7 pares
               idénticos se desplazan juntos porque representan la misma cantidad). Destruye la
               coordinación temporal entre aristas.
  permutacion: permuta qué serie va en qué arista temporal (las 125 aristas estáticas no cambian).
               Conserva la coordinación temporal pero la coloca en otra parte de la red.
Inversión temporal: NO es un nulo. Es una comprobación exacta: A, omega y Gamma cambian de signo;
  |u|^2, P y por tanto V no cambian. Se reporta la diferencia numérica.

Estadísticos (comunes.estadisticos_globales):
  sin kernel: A_total, A_abs, coherencia, A_max_abs
  con kernel (h = 0.35): omega_media_P, omega_abs_P, flujo_sobre_bohm_l1, masa_J_en_mascara, div_rel
  div_rel se reporta como diagnóstico, no se contrasta.
Valor p bilateral empírico: p = min(1, 2 min(#{nulo >= obs} + 1, #{nulo <= obs} + 1) / (n + 1)).
Holm-Bonferroni por familia (primaria = A_total, coherencia, omega_media_P; secundaria = el resto,
exploratoria) y por clustering. Por defecto 400 réplicas por nulo.

Kernel solo con Barrat (estado principal). Con Onnela se usan solo los estadísticos sin kernel
(refine 20, requerido por subpaso < h), para que el tiempo total sea razonable.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

from campos import malla
from comunes import estadisticos_globales
from phasik import cargar_series, construir_W, refinar_tiempo, trayectorias

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
SEED = 12345
H = 0.35
N_GRID = 40
REFINE = {"barrat": 10, "onnela": 20}
CON_KDE = {"barrat": True, "onnela": False}
# Familia primaria declarada de antemano (circulación y vorticidad media). Holm se aplica por
# separado a cada familia y clustering. Con 400 réplicas, p mínimo = 2/401 y, con 6 contrastes
# primarios (3 x 2 nulos), p_holm mínimo = 0.03.
PRIMARIOS = ["A_total", "coherencia", "omega_media_P"]
SECUNDARIOS = ["A_abs", "A_max_abs", "omega_abs_P", "flujo_sobre_bohm_l1", "masa_J_en_mascara"]
# POST HOC: añadidos tras ver (con 50 réplicas) que flujo_sobre_bohm_l1 superaba a todas las réplicas.
# Sirven para separar numerador (solo u: línea base) y denominador (solo P: Bohm). Familia propia.
SEGUIMIENTO = ["u_max_mascara", "rango_flujo", "rango_bohm1"]
CONTRASTADOS = PRIMARIOS + SECUNDARIOS + SEGUIMIENTO
FAMILIA = {**{k: "primaria" for k in PRIMARIOS}, **{k: "secundaria" for k in SECUNDARIOS},
           **{k: "seguimiento_post_hoc" for k in SEGUIMIENTO}}


def grupos_identicos(X):
    claves = {}
    for j in range(X.shape[1]):
        claves.setdefault(X[:, j].round(12).tobytes(), []).append(j)
    return list(claves.values())


def nulo_desfase(X, grupos, rng):
    Y = X.copy()
    T = X.shape[0]
    for g in grupos:
        Y[:, g] = np.roll(X[:, g], rng.integers(T), axis=0)
    return Y


def nulo_permutacion(X, rng):
    return X[:, rng.permutation(X.shape[1])]


def estado(X, nombres, clus):
    W, _, _ = construir_W(nombres, X)
    r, _ = trayectorias(refinar_tiempo(W, REFINE[clus]), clus)
    return r


def valor_p(obs, nulo):
    nulo = np.asarray(nulo)
    nulo = nulo[np.isfinite(nulo)]
    n = len(nulo)
    if n == 0 or not np.isfinite(obs):
        return np.nan
    return min(1.0, 2 * min((nulo >= obs).sum() + 1, (nulo <= obs).sum() + 1) / (n + 1))


def holm(p):
    p = np.asarray(p, float)
    ok = np.isfinite(p)
    out = np.full_like(p, np.nan)
    idx = np.argsort(p[ok])
    pv = p[ok][idx]
    m = len(pv)
    adj = np.maximum.accumulate(np.minimum(1.0, (m - np.arange(m)) * pv))
    tmp = np.empty(m)
    tmp[idx] = adj
    out[ok] = tmp
    return out


def main(n_rep=200):
    nombres, X = cargar_series(cierre="ninguna")
    grupos = grupos_identicos(X)
    print(f"Grupos de series idénticas: {len(grupos)} (de {X.shape[1]} series)")
    resumen, crudo, inversion = [], [], []
    for clus in REFINE:
        t0 = time.time()
        r_obs = estado(X, nombres, clus)
        S = r_obs.reshape(-1, 2)
        _, _, G = malla(S.min(0) - 1.5, S.max(0) + 1.5, N_GRID)   # margen extra: los nulos se mueven algo más
        obs = estadisticos_globales(r_obs, G, H, CON_KDE[clus])

        # inversión temporal (comprobación exacta)
        rev = estadisticos_globales(r_obs[::-1].copy(), G, H, CON_KDE[clus])
        for k in obs:
            inversion.append(dict(clustering=clus, estadistico=k, observado=obs[k], invertido=rev[k],
                                  esperado="-obs" if k in ("A_total", "omega_media_P") else "igual"))

        rng = np.random.default_rng(SEED)
        for nombre_nulo in ("desfase", "permutacion"):
            for rep in range(n_rep):
                Xn = nulo_desfase(X, grupos, rng) if nombre_nulo == "desfase" else nulo_permutacion(X, rng)
                st = estadisticos_globales(estado(Xn, nombres, clus), G, H, CON_KDE[clus])
                crudo.append(dict(clustering=clus, nulo=nombre_nulo, rep=rep, **st))
            print(f"  {clus} {nombre_nulo}: {n_rep} réplicas, {time.time() - t0:.0f} s acumulados")

        df_c = pd.DataFrame([c for c in crudo if c["clustering"] == clus])
        filas = []
        for nombre_nulo in ("desfase", "permutacion"):
            d = df_c[df_c.nulo == nombre_nulo]
            for k in CONTRASTADOS:
                if k not in obs:
                    continue
                v = d[k].to_numpy()
                filas.append(dict(clustering=clus, nulo=nombre_nulo, estadistico=k,
                                  familia=FAMILIA[k], observado=obs[k],
                                  nulo_mediana=np.nanmedian(v), nulo_p2_5=np.nanpercentile(v, 2.5),
                                  nulo_p97_5=np.nanpercentile(v, 97.5),
                                  z=(obs[k] - np.nanmean(v)) / np.nanstd(v) if np.nanstd(v) > 0 else np.nan,
                                  p=valor_p(obs[k], v)))
        for fam in ("primaria", "secundaria", "seguimiento_post_hoc"):
            sub = [f for f in filas if f["familia"] == fam]
            for f, q in zip(sub, holm([f["p"] for f in sub])):
                f["p_holm"] = q
        resumen += filas

    os.makedirs(OUT, exist_ok=True)
    pd.DataFrame(crudo).to_csv(os.path.join(OUT, "b5_nulos_replicas.csv"), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print("\n=== Inversión temporal (comprobación, no nulo) ===")
        di = pd.DataFrame(inversion)
        di.to_csv(os.path.join(OUT, "b5_inversion.csv"), index=False)
        print(di.to_string(index=False, float_format=lambda v: f"{v:.6g}"))
        print(f"\n=== Observado frente a nulos ({n_rep} réplicas; p bilateral; Holm por clustering) ===")
        dr = pd.DataFrame(resumen)
        dr.to_csv(os.path.join(OUT, "b5_nulos_resumen.csv"), index=False)
        print(dr.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
