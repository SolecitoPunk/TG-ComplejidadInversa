"""
Bloque 6: barridos de sensibilidad y estabilidad de mínimos corregida por azar.

    python b6_barridos.py

Tabla 1 (b6_estabilidad_azar.csv): repite la prueba de estabilidad del bloque 3 y añade la tasa de
  emparejamiento por azar. Si los K_TOP mínimos de referencia estuvieran en puntos al azar de la
  máscara, la probabilidad de que cada uno tenga pareja es la fracción del área de la máscara a menos
  de D_MATCH de algún mínimo de la configuración perturbada ('azar'). Exceso = emparejados - azar.
  Así se corrige el sesgo a favor de campos con muchos mínimos (V_B tiene unas 3 veces más que U).
Tabla 2 (b6_sensibilidad.csv): estadísticos globales y número de mínimos relevantes frente a
  h, tamaño de malla y TIME_REFINE. La dependencia en lambda está en las columnas nrel_V(l=...).
Referencias: Barrat refine 10; Onnela refine 20 (condición subpaso < h, bloque 3).
"""
import os
import time

import numpy as np
import pandas as pd

from campos import malla
from comunes import campos_rapidos, estadisticos_globales, MASK_FRAC
from b3_linea_base import (preparar, campos_escalares, minimos_persistentes, top_minimos, emparejar,
                           H_REF, D_MATCH, PERS_MIN)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
REF = {"barrat": 10, "onnela": 20}
HS = (0.25, 0.35, 0.5)
GRIDS = (40, 60, 80)


def _imprimir(df, nombre):
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, nombre), index=False)
    with pd.option_context("display.width", 260, "display.max_columns", 40):
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


def _malla(r, n):
    S = r.reshape(-1, 2)
    return malla(S.min(0) - 1.0, S.max(0) + 1.0, n)


def evaluar(r, X, Y, G, h):
    F = campos_rapidos(r, G, h)
    mask = F["P"] > MASK_FRAC * F["P"].max()
    Z = campos_escalares(F, X.shape)
    m2 = mask.reshape(X.shape)
    res = {}
    for nombre, Zc in Z.items():
        mins = minimos_persistentes(Zc, m2)
        res[nombre] = dict(top=top_minimos(mins, X, Y),
                           nmin=sum(1 for mm in mins if not mm["borde"]),
                           nrel=sum(1 for mm in mins if not mm["borde"] and mm["pers_rel"] >= PERS_MIN))
    return F, m2, res


def tabla_estabilidad():
    filas = []
    for clus, ref in REF.items():
        t0 = time.time()
        r_ref, _ = preparar(clus, ref)
        X, Y, G = _malla(r_ref, 60)
        _, m_ref, res_ref = evaluar(r_ref, X, Y, G, H_REF)
        celdas = np.column_stack([X[m_ref], Y[m_ref]])
        for tipo, val in (("h", 0.25), ("h", 0.5), ("refine", ref // 2), ("refine", ref * 2)):
            h = val if tipo == "h" else H_REF
            r = r_ref if tipo == "h" else preparar(clus, val)[0]
            _, _, res = evaluar(r, X, Y, G, h)
            for nombre in res_ref:
                pos_p, pers_p = res[nombre]["top"]
                frac, dp = emparejar(*res_ref[nombre]["top"], pos_p, pers_p)
                if len(pos_p):
                    azar = float((np.linalg.norm(celdas[:, None] - pos_p[None], axis=-1).min(1) < D_MATCH).mean())
                else:
                    azar = 0.0
                filas.append(dict(clustering=clus, perturbacion=f"{tipo}={val}", campo=nombre,
                                  n_ref=len(res_ref[nombre]["top"][0]), frac_emparejados=frac, azar=azar,
                                  exceso=frac - azar, dpers_rel_mediana=dp))
        print(f"  estabilidad {clus}: {time.time() - t0:.1f} s")
    df = pd.DataFrame(filas)
    _imprimir(df, "b6_estabilidad_azar.csv")
    print("\nExceso medio sobre el azar (solo perturbaciones de h; refine no mueve los mínimos):")
    sub = df[df.perturbacion.str.startswith("h=")]
    with pd.option_context("display.width", 200):
        print(sub.pivot_table(index="campo", columns="clustering", values=["frac_emparejados", "azar", "exceso"],
                              aggfunc="mean").to_string(float_format=lambda v: f"{v:.2f}"))
    return df


def tabla_sensibilidad():
    filas = []
    for clus, ref in REF.items():
        t0 = time.time()
        configs = [(h, n, ref) for h in HS for n in GRIDS] + [(H_REF, 60, ref // 2), (H_REF, 60, ref * 2)]
        cache = {}
        for h, n, refine in configs:
            if refine not in cache:
                cache[refine] = preparar(clus, refine)[0]
            r = cache[refine]
            X, Y, G = _malla(cache[ref], n)
            F, m2, res = evaluar(r, X, Y, G, h)
            st = estadisticos_globales(r, G, h, con_kde=True)
            fila = dict(clustering=clus, h=h, malla=n, refine=refine,
                        subpaso_max_sobre_h=np.linalg.norm(np.diff(r, axis=0), axis=-1).max() / h)
            fila.update({k: st[k] for k in ("div_rel", "masa_J_en_mascara", "flujo_sobre_bohm_l1",
                                            "u_max_mascara", "omega_media_P", "A_total")})
            for nombre, v in res.items():
                fila[f"nrel_{nombre}"] = v["nrel"]
            filas.append(fila)
        print(f"  sensibilidad {clus}: {time.time() - t0:.1f} s")
    _imprimir(pd.DataFrame(filas), "b6_sensibilidad.csv")


if __name__ == "__main__":
    t0 = time.time()
    print("=== Estabilidad de mínimos con tasa de azar ===")
    tabla_estabilidad()
    print("\n=== Sensibilidad ===")
    tabla_sensibilidad()
    print(f"[b6] {time.time() - t0:.1f} s")
