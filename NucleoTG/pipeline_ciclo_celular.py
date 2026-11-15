"""
Pipeline: ecuación extendida (Ec. 11) sobre una red temporal con un ciclo periódico.

Idea:
  - Cada nodo i tiene en cada instante t un estado r_i(t) = (log(1+s_i), C_i) en un plano 2D
    (s = fuerza ponderada, C = clustering ponderado de Onnela).
  - Promediando sobre UN ciclo completo se obtienen la densidad P(r) y la corriente J(r).
  - Para trayectorias cerradas, div J = 0 (continuidad estacionaria, análoga a la Ec. 9).
  - u = J/P es el flujo cinético medido (u = grad S - qA, invariante de gauge).
  - V(r) = E - |u|^2/(2m) + (hbar^2/4m) [ lap P / P - 1/2 |grad P|^2 / P^2 ]   (Ec. 11)
  - La vorticidad de u, rot(u), es la cantidad invariante de gauge (equivale a -qB).

Parámetros libres (hay que reportarlos): H_BANDWIDTH y LAMBDA (= hbar^2/m, con m = 1).
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import minimum_filter

# ============================================================
# PARÁMETROS LIBRES
# ============================================================
H_BANDWIDTH = 0.35   # ancho del kernel gaussiano (en unidades estandarizadas)
LAMBDA = 1.0         # lambda = hbar^2/m ; fija el peso relativo Bohm vs flujo
GRID = 70            # puntos por eje de la malla
MASK_FRAC = 0.05     # se enmascara donde P < MASK_FRAC * P.max()
USE_TOY = False      # True: red sintética periódica de prueba (sin necesitar datos)
DATA_DIR = "data"    # carpeta data/ del repo de Phasik (usa "../data" si corres desde notebooks/)
STATIC_EDGE_WEIGHT = 1.0      # peso de aristas sin serie temporal (default de Phasik)
DROP_LAST_SNAPSHOT = False    # True si el último instante repite el primero (t=101 = t=0)
TIME_REFINE = 10     # subdivisiones temporales (interpolación lineal periódica de los pesos)
CLUSTERING = "onnela"  # "onnela" (raíz cúbica de pesos) o "barrat" (lineal en pesos, topología fija)
NODE_NAMES = None    # lo rellena el cargador (nombres de proteínas)


# ============================================================
# 1. DATOS
# ============================================================
def toy_periodic_network(N=60, T=101, p=0.15, seed=0):
    """Red sintética con pesos periódicos (un ciclo de T pasos). SOLO para probar el código."""
    rng = np.random.default_rng(seed)
    base = np.triu((rng.random((N, N)) < p) * rng.uniform(0.5, 1.5, (N, N)), 1)
    phase = np.triu(rng.uniform(0, 2 * np.pi, (N, N)), 1)
    amp = np.triu(rng.uniform(0.3, 0.9, (N, N)), 1)
    t = np.arange(T)[:, None, None]
    W = np.clip(base * (1 + amp * np.sin(2 * np.pi * t / T + phase)), 0, None)
    return W + W.transpose(0, 2, 1)


def load_temporal_network():
    """Construye W (T, N, N) a partir de los archivos de Phasik (mismo formato que el notebook 1_b):
      - red estática KEGG:  <DATA_DIR>/kegg/static_PPI_network_KEGG.adjlist
      - series de aristas:  <DATA_DIR>/chen/edge_time_series_normed.csv  (columnas = 'A-B', filas = tiempos)
    Las aristas sin serie temporal reciben peso constante STATIC_EDGE_WEIGHT (Phasik usa 1)."""
    import os
    import networkx as nx
    import pandas as pd

    G = nx.read_adjlist(os.path.join(DATA_DIR, "kegg", "static_PPI_network_KEGG.adjlist"))
    es = pd.read_csv(os.path.join(DATA_DIR, "chen", "edge_time_series_normed.csv")).transpose()
    T = es.shape[1]
    global NODE_NAMES
    nodes = sorted(G.nodes())
    NODE_NAMES = nodes
    idx = {n: i for i, n in enumerate(nodes)}
    W = np.zeros((T, len(nodes), len(nodes)))
    n_temporal = 0
    for u, v in G.edges():
        if u == v:
            continue
        key = next((k for k in (f"{u}-{v}", f"{v}-{u}") if k in es.index), None)
        if key is not None:
            ser = es.loc[key]
            ser = ser.iloc[0] if ser.ndim > 1 else ser
            w = ser.to_numpy(dtype=float)
            n_temporal += 1
        else:
            w = np.full(T, STATIC_EDGE_WEIGHT)
        W[:, idx[u], idx[v]] = w
        W[:, idx[v], idx[u]] = w
    print(f"Red cargada: {len(nodes)} nodos, {G.number_of_edges()} aristas, "
          f"{n_temporal} temporales, {T} instantes")
    if n_temporal != es.shape[0]:
        print(f"AVISO: el CSV tiene {es.shape[0]} series pero solo {n_temporal} casaron con aristas "
              f"de la red estática; revisa los nombres ('A-B').")
    if DROP_LAST_SNAPSHOT:
        W = W[:-1]
    return W


def refine_time(W, f):
    """Interpolación lineal periódica de los pesos en el tiempo (f subdivisiones por paso).
    No añade información: reduce el error de discretización de la corriente J (con 102 pasos,
    la divergencia residual de J baja de ~0.33 a ~0.04 al pasar de f=1 a f=10 en datos simulados)."""
    if f <= 1:
        return W
    T = W.shape[0]
    tt = np.arange(T * f) / f
    i0 = np.floor(tt).astype(int) % T
    i1 = (i0 + 1) % T
    a = (tt - np.floor(tt))[:, None, None]
    return (1 - a) * W[i0] + a * W[i1]


# ============================================================
# 2. ESTADO 2D POR NODO Y TIEMPO
# ============================================================
def node_state(W):
    """x = log(1 + fuerza ponderada s). C = clustering ponderado, según CLUSTERING:
      - "onnela": media geométrica de pesos (raíz cúbica); muy sensible a pesos cercanos a 0.
      - "barrat": lineal en los pesos y con la topología fija de la PPI (aristas = las que alguna vez
                  tienen peso > 0); no tiene saltos por aristas que aparecen/desaparecen."""
    s = W.sum(axis=2)                              # (T, N)
    if CLUSTERING == "barrat":
        A = (W.max(axis=0) > 0).astype(float)      # topología fija (N, N)
        k = A.sum(axis=1)                          # grado estático
        tri = (W * (A * (A @ A))[None]).sum(axis=2)
        C = np.where(k > 1, tri / (np.maximum(s, 1e-12) * np.maximum(k - 1, 1)), 0.0)
    else:                                          # Onnela et al. 2005
        k = (W > 0).sum(axis=2)
        R = np.cbrt(W / W.max())
        tri = np.einsum('tij,tjk,tki->ti', R, R, R)
        denom = k * (k - 1)
        C = np.where(denom > 0, tri / np.maximum(denom, 1), 0.0)
    return np.log1p(s), C


def build_samples(W):
    x, C = node_state(W)
    r = np.stack([x, C], axis=-1)                  # (T, N, 2)
    mu, sd = r.reshape(-1, 2).mean(0), r.reshape(-1, 2).std(0)
    r = (r - mu) / sd                              # coordenadas estandarizadas
    T = r.shape[0]
    v = (np.roll(r, -1, axis=0) - r) * T           # velocidad con tiempo normalizado al periodo (ciclo = 1)
    step = np.linalg.norm(r[1:] - r[:-1], axis=-1)       # (T-1, N)
    gap = np.linalg.norm(r[0] - r[-1], axis=-1)          # (N,)
    moving = step.sum(axis=0) > 1e-9                     # nodos que realmente se mueven en el plano
    print(f"Nodos que se mueven en el plano (r cambia en el ciclo): {moving.sum()} de {moving.size}")
    closure = gap[moving].mean() / np.median(step[:, moving])   # >> 1 => los datos NO son periódicos
    ref = np.median(step[:, moving])
    names = NODE_NAMES if NODE_NAMES is not None else list(range(r.shape[1]))
    big = step.max(axis=0) / ref
    top = np.argsort(-big)[:5]
    print("Mayores saltos en un solo paso (en pasos típicos): " +
          ", ".join(f"{names[i]}={big[i]:.0f}" for i in top))
    topg = np.argsort(-gap)[:5]
    print("Mayores brechas de cierre (en pasos típicos):      " +
          ", ".join(f"{names[i]}={gap[i] / ref:.0f}" for i in topg))
    return r.reshape(-1, 2), v.reshape(-1, 2), closure


# ============================================================
# 3. CAMPOS CON KERNEL GAUSSIANO (derivadas ANALÍTICAS, sin diferencias finitas)
# ============================================================
def kernel_fields(G, S, Vel, h, chunk=50):
    n = G.shape[0]
    P = np.zeros(n); gP = np.zeros((n, 2)); lP = np.zeros(n)
    J = np.zeros((n, 2)); dJ = np.zeros(n)
    for a in range(0, n, chunk):
        d = G[a:a + chunk, None, :] - S[None, :, :]
        q = (d ** 2).sum(-1) / h ** 2
        K = np.exp(-0.5 * q) / (2 * np.pi * h ** 2)
        P[a:a + chunk] = K.mean(1)
        gP[a:a + chunk] = -(K[..., None] * d).mean(1) / h ** 2
        lP[a:a + chunk] = (K * (q - 2)).mean(1) / h ** 2
        J[a:a + chunk] = (K[..., None] * Vel[None]).mean(1)
        dJ[a:a + chunk] = -(K * (d * Vel[None]).sum(-1)).mean(1) / h ** 2
    return P, gP, lP, J, dJ


def lambda_sweep(P, gP, lP, flow, mask, shape):
    """Muestra cómo cambian el peso del flujo y la topología de V al variar lambda = hbar^2/m."""
    eps = 1e-12
    bohm1 = 0.25 * (lP / (P + eps) - 0.5 * (gP ** 2).sum(1) / (P + eps) ** 2)
    m2 = mask.reshape(shape)
    print("\nlambda   rango(flujo)/rango(Bohm)   n.º de mínimos locales de V")
    for lam in (1, 0.3, 0.1, 0.03, 0.01, 0.003):
        Vl = lam * bohm1 + flow
        Vg = np.where(m2, Vl.reshape(shape), np.inf)
        nmin = int(((Vg == minimum_filter(Vg, size=5, mode="nearest")) & m2).sum())
        ratio = np.ptp(flow[mask]) / np.ptp(lam * bohm1[mask])
        print(f"{lam:<8} {ratio:>12.3f}              {nmin:>6d}")
    print()


def main():
    W = toy_periodic_network() if USE_TOY else load_temporal_network()
    W = refine_time(W, TIME_REFINE)
    S, Vel, closure = build_samples(W)

    lo, hi = S.min(0) - 1.0, S.max(0) + 1.0
    xg = np.linspace(lo[0], hi[0], GRID)
    yg = np.linspace(lo[1], hi[1], GRID)
    X, Y = np.meshgrid(xg, yg)
    G = np.column_stack([X.ravel(), Y.ravel()])

    P, gP, lP, J, dJ = kernel_fields(G, S, Vel, H_BANDWIDTH)
    eps = 1e-12
    mask = P > MASK_FRAC * P.max()

    u = J / (P[:, None] + eps)                                       # flujo cinético medido
    bohm = 0.25 * LAMBDA * (lP / (P + eps) - 0.5 * (gP ** 2).sum(1) / (P + eps) ** 2)
    flow = -0.5 * (u ** 2).sum(1)
    V = bohm + flow

    # ---- diagnósticos ----
    rel_div = np.sqrt((dJ[mask] ** 2).mean()) / (np.sqrt((J[mask] ** 2).sum(1).mean()) / H_BANDWIDTH)
    print(f"Cierre del ciclo (salto de cierre / paso típico): {closure:.2f}  (~1 es OK; >>1 = no periódico)")
    print(f"Divergencia relativa de J (estacionariedad):      {rel_div:.3f}  (cerca de 0 es OK)")
    print(f"Rango término Bohm: [{bohm[mask].min():.3f}, {bohm[mask].max():.3f}]")
    print(f"Rango término flujo: [{flow[mask].min():.3f}, {flow[mask].max():.3f}]")

    shape = X.shape
    lambda_sweep(P, gP, lP, flow, mask, shape)
    ux, uy = u[:, 0].reshape(shape), u[:, 1].reshape(shape)
    dx, dy = xg[1] - xg[0], yg[1] - yg[0]
    omega = np.gradient(uy, dx, axis=1) - np.gradient(ux, dy, axis=0)   # rot(u) = -qB
    m2 = mask.reshape(shape)
    Pm = np.where(m2, P.reshape(shape), np.nan)
    om = np.where(m2, omega, np.nan)
    Vm = np.where(m2, V.reshape(shape), np.nan)
    Vm = Vm - np.nanmin(Vm)

    fig = plt.figure(figsize=(14, 11))
    ax = axA = fig.add_subplot(2, 2, 1)
    c = ax.contourf(X, Y, Pm, 20, cmap='magma')
    ax.scatter(S[::7, 0], S[::7, 1], s=2, c='cyan', alpha=0.25)
    ax.set_title(r"A. Densidad media en un ciclo $\bar P(\mathbf{r})$")
    fig.colorbar(c, ax=ax)

    ax = axB = fig.add_subplot(2, 2, 2)
    ax.contourf(X, Y, Pm, 20, cmap='Greys', alpha=0.6)
    s = 3
    ax.quiver(X[::s, ::s], Y[::s, ::s],
              np.where(m2, ux, np.nan)[::s, ::s], np.where(m2, uy, np.nan)[::s, ::s],
              color='crimson')
    ax.set_title(r"B. Flujo medido $\mathbf{u}=\mathbf{J}/P$ (promedio en un ciclo)")

    ax = axC = fig.add_subplot(2, 2, 3)
    lim = np.nanpercentile(np.abs(om), 95)
    c = ax.contourf(X, Y, om, 21, cmap='RdBu_r', vmin=-lim, vmax=lim)
    ax.set_title(r"C. Vorticidad $\nabla\times\mathbf{u}$ (invariante de gauge)")
    fig.colorbar(c, ax=ax)

    ax3 = fig.add_subplot(2, 2, 4, projection='3d')
    ax3.plot_surface(X, Y, Vm, cmap='viridis_r', linewidth=0, antialiased=True)
    ax3.set_title(r"D. Paisaje $V(\mathbf{r})$ (Ec. 11)")
    ax3.view_init(elev=35, azim=230)

    for a in (axA, axB, axC):
        a.set_xlabel(r"$\log(1+s)$ (estandarizado)")
        a.set_ylabel(r"$C$ (estandarizado)")
    plt.tight_layout()
    plt.savefig(f"resultado_ciclo_{CLUSTERING}.png", dpi=200, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        CLUSTERING = sys.argv[1]     # python pipeline_ciclo_celular.py barrat
    main()
