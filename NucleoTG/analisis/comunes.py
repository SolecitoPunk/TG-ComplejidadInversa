"""
comunes.py: piezas compartidas por los bloques 4-6.

- campos_rapidos: mismos campos que en el bloque 3, pero cada nodo estático entra como un
  punto con peso T y las muestras con velocidad cero no se suman a J. El resultado es
  matemáticamente idéntico; solo cambia el coste.
- estadisticos_globales: resúmenes escalares (no dependen de un punto de malla) para nulos y barridos.
"""
import numpy as np

from campos import muestras, densidad_kde, corriente_kde, campos_derivados, div_relativa

MASK_FRAC = 0.05


def separar_nodos(r, tol=1e-9):
    """Máscara booleana (N,) de nodos que se mueven en el plano."""
    return np.linalg.norm(np.diff(r, axis=0), axis=-1).sum(0) > tol


def campos_rapidos(r, G, h, poblacion="todos"):
    """poblacion: 'todos' (P y J de todos los nodos), 'moviles' (solo los que se mueven),
    'estaticos' (solo P de los estáticos; J = 0)."""
    T, N, _ = r.shape
    mov = separar_nodos(r)
    if poblacion == "moviles":
        sel_mov, sel_sta = mov, np.zeros(N, bool)
    elif poblacion == "estaticos":
        sel_mov, sel_sta = np.zeros(N, bool), ~mov
    elif poblacion == "todos":
        sel_mov, sel_sta = mov, ~mov
    else:
        raise ValueError(poblacion)
    n_pob = int(sel_mov.sum() + sel_sta.sum())
    partes_A, partes_w = [], []
    if sel_mov.any():
        A_m, B_m, V_m = muestras(r[:, sel_mov], 1.0 / T, "medio", cerrado=True)
        partes_A.append(A_m)
        partes_w.append(np.ones(len(A_m)))
    if sel_sta.any():
        partes_A.append(r[0, sel_sta])
        partes_w.append(np.full(int(sel_sta.sum()), float(T)))
    A = np.vstack(partes_A)
    P, gP, lP = densidad_kde(G, A, h, pesos=np.concatenate(partes_w))
    if sel_mov.any():
        J, gJ = corriente_kde(G, B_m, V_m, h, n_total=n_pob * T)
    else:
        J, gJ = np.zeros((len(G), 2)), np.zeros((len(G), 2, 2))
    return campos_derivados(P, gP, lP, J, gJ)


def areas_con_signo(r):
    r1 = np.roll(r, -1, axis=0)
    return 0.5 * (r[..., 0] * r1[..., 1] - r1[..., 0] * r[..., 1]).sum(0)


def estadisticos_globales(r, G, h, con_kde=True):
    """Resúmenes escalares. Los de área no usan kernel; los de vorticidad y flujo sí."""
    mov = separar_nodos(r)
    Ai = areas_con_signo(r)[mov]
    out = dict(A_total=Ai.sum(), A_abs=np.abs(Ai).sum(),
               coherencia=abs(Ai.sum()) / np.abs(Ai).sum() if np.abs(Ai).sum() > 0 else np.nan,
               A_max_abs=np.abs(Ai).max() if len(Ai) else np.nan)
    if con_kde:
        F = campos_rapidos(r, G, h)
        m = F["P"] > MASK_FRAC * F["P"].max()
        Pm = F["P"][m]
        Jn = np.linalg.norm(F["J"], axis=1)
        out.update(
            u_max_mascara=float(np.sqrt(-2 * F["flujo"][m].min())),
            rango_flujo=float(np.ptp(F["flujo"][m])),
            rango_bohm1=float(np.ptp(F["bohm1"][m])),
            omega_media_P=float((Pm * F["omega"][m]).sum() / Pm.sum()),
            omega_abs_P=float((Pm * np.abs(F["omega"][m])).sum() / Pm.sum()),
            flujo_sobre_bohm_l1=float(np.ptp(F["flujo"][m]) / np.ptp(F["bohm1"][m])),
            masa_J_en_mascara=float(Jn[m].sum() / Jn.sum()) if Jn.sum() > 0 else np.nan,
            div_rel=float(div_relativa(F, m, h)),
        )
    return out
