"""
Bloque 4: separar la dinámica de la estructura estática.

    python b4_separacion.py

Para cada clustering (referencia: h = 0.35, refine 10 con Barrat y 20 con Onnela, porque con
refine 10 Onnela viola subpaso < h; ver bloque 3), se calculan los campos con tres poblaciones:
  todos     : como en el bloque 3
  moviles   : solo los nodos que se mueven (P y J de ellos; u = velocidad media real de los móviles)
  estaticos : solo los nodos estáticos (P; sin corriente)
Con 'todos', u = J/P está diluida por la densidad de los estáticos donde se solapan.

Tablas:
  b4_poblaciones.csv : masa, flujo/Bohm, número de mínimos de U, V_B y V(l) por población
  b4_origen_minimos.csv : ¿los mínimos más persistentes de la población 'todos' aparecen en
                          'estaticos' o en 'moviles'? (misma regla de emparejamiento que el bloque 3)
  b4_estaticos.csv : posiciones distintas de los nodos estáticos y cuántas están separadas > h
Comprobación: campos_rapidos('todos') debe coincidir con el cálculo directo del bloque 3 (~1e-12).
"""
import os
import time

import numpy as np
import pandas as pd

from campos import malla
from comunes import campos_rapidos, separar_nodos, MASK_FRAC
from b3_linea_base import (preparar, campos_en_malla, campos_escalares, minimos_persistentes,
                           top_minimos, emparejar, N_GRID, H_REF, D_MATCH, PERS_MIN)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
REFINE = {"barrat": 10, "onnela": 20}
POBLACIONES = ("todos", "moviles", "estaticos")


def _imprimir(df, nombre):
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, nombre), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 40):
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


def main():
    f_pob, f_ori, f_sta = [], [], []
    for clus, refine in REFINE.items():
        t0 = time.time()
        r, nodos = preparar(clus, refine)
        S = r.reshape(-1, 2)
        X, Y, G = malla(S.min(0) - 1.0, S.max(0) + 1.0, N_GRID)
        mov = separar_nodos(r)

        F_dir = campos_en_malla(r, G, H_REF)
        F_rap = campos_rapidos(r, G, H_REF, "todos")
        dif = max(np.max(np.abs(F_rap[k] - F_dir[k])) / np.max(np.abs(F_dir[k])) for k in ("P", "J", "lP"))
        print(f"{clus}: comprobación rápido frente a directo, diferencia relativa máxima = {dif:.2e}")

        sta_pos = r[0, ~mov]
        uniq = np.unique(sta_pos.round(9), axis=0)
        dd = np.linalg.norm(uniq[:, None] - uniq[None], axis=-1) + np.eye(len(uniq)) * 1e9
        f_sta.append(dict(clustering=clus, n_estaticos=int((~mov).sum()), posiciones_distintas=len(uniq),
                          aisladas_mas_de_h=int((dd.min(1) > H_REF).sum()),
                          nodos_por_posicion_max=int(max((np.all(sta_pos.round(9) == u, axis=1)).sum() for u in uniq))))

        tops = {}
        for pob in POBLACIONES:
            F = campos_rapidos(r, G, H_REF, pob)
            mask = F["P"] > MASK_FRAC * F["P"].max()
            Z = campos_escalares(F, X.shape)
            if pob == "estaticos":
                Z = {k: v for k, v in Z.items() if k in ("U", "V_B")}
            m2 = mask.reshape(X.shape)
            Jn = np.linalg.norm(F["J"], axis=1)
            fila = dict(clustering=clus, poblacion=pob, refine=refine,
                        nodos=int({"todos": len(mov), "moviles": mov.sum(), "estaticos": (~mov).sum()}[pob]),
                        masa_J_en_mascara=Jn[mask].sum() / Jn.sum() if Jn.sum() > 0 else np.nan,
                        flujo_sobre_bohm_l1=np.ptp(F["flujo"][mask]) / np.ptp(F["bohm1"][mask]),
                        u_max_en_mascara=np.sqrt(-2 * F["flujo"][mask].min()))
            tops[pob] = {}
            for nombre, Zc in Z.items():
                mins = minimos_persistentes(Zc, m2)
                tops[pob][nombre] = top_minimos(mins, X, Y)
                fila[f"nmin_{nombre}"] = sum(1 for mm in mins if not mm["borde"])
                fila[f"nrel_{nombre}"] = sum(1 for mm in mins if not mm["borde"] and mm["pers_rel"] >= PERS_MIN)
            f_pob.append(fila)

        for nombre in tops["todos"]:
            fila = dict(clustering=clus, campo=nombre)
            for pob in ("estaticos", "moviles"):
                if nombre in tops[pob]:
                    fila[f"frac_en_{pob}"], _ = emparejar(*tops["todos"][nombre], *tops[pob][nombre])
                else:
                    fila[f"frac_en_{pob}"] = np.nan
            f_ori.append(fila)
        print(f"  {clus}: {time.time() - t0:.1f} s")

    print("\n=== Nodos estáticos ===")
    _imprimir(pd.DataFrame(f_sta), "b4_estaticos.csv")
    print("\n=== Campos por población ===")
    _imprimir(pd.DataFrame(f_pob), "b4_poblaciones.csv")
    print(f"\n=== Origen de los mínimos más persistentes de 'todos' (pareja a < {D_MATCH}) ===")
    _imprimir(pd.DataFrame(f_ori), "b4_origen_minimos.csv")


if __name__ == "__main__":
    main()
