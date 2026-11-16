"""
phasik.py: carga de la red temporal (Phasik / modelo de Chen) y estados 2D por nodo.

Reconstruye W[t, i, j] directamente desde los dos archivos de NucleoTG/:
  - static_PPI_network_KEGG.adjlist  (83 nodos, 159 aristas)
  - edge_time_series_normed.csv      (102 filas = tiempos, 34 columnas = aristas "A-B")
Las aristas sin serie temporal reciben `peso_estatico` (Phasik usa 1).

Hechos verificados sobre el CSV (ver RESULTADOS_bloque2.md):
  - cada serie está dividida por su máximo (max = 1 en las 34; ningún mínimo es 0);
  - hay 7 pares de series idénticas;
  - ningún peso es exactamente 0, así que el grado k_i(t) es constante.
"""
import os

import numpy as np
import pandas as pd
import networkx as nx

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # NucleoTG/
ADJ = "static_PPI_network_KEGG.adjlist"
CSV = "edge_time_series_normed.csv"
CIERRES = ("ninguna", "droplast", "lineal")


def cargar_series(data_dir=DATA_DIR, cierre="ninguna"):
    """Devuelve (nombres de arista, X (T, E)).
    cierre:
      'ninguna'  : datos tal cual (t = 0..101; el segmento 101 -> 0 cierra el ciclo).
      'droplast' : descarta t = 101 (el ciclo se cierra con 100 -> 0).
      'lineal'   : MODIFICA los datos. Resta una rampa para que el valor extrapolado
                   x(T) = 2 x(T-1) - x(T-2) coincida con x(0):
                       x'(t) = x(t) - (t/T) [x(T) - x(0)]
                   y acota cada serie por debajo con su mínimo original (no crea ceros)."""
    es = pd.read_csv(os.path.join(data_dir, CSV))
    X = es.to_numpy(dtype=float)
    if cierre == "droplast":
        X = X[:-1]
    elif cierre == "lineal":
        T = len(X)
        delta = (2 * X[-1] - X[-2]) - X[0]
        X = np.maximum(X - (np.arange(T)[:, None] / T) * delta[None, :], X.min(axis=0))
    elif cierre != "ninguna":
        raise ValueError(f"cierre desconocido: {cierre!r}")
    return list(es.columns), X


def construir_W(nombres, X, data_dir=DATA_DIR, peso_estatico=1.0):
    """W (T, N, N) simétrica. Devuelve W, nodos (orden alfabético), aristas temporales [(i, j, col)]."""
    G = nx.read_adjlist(os.path.join(data_dir, ADJ))
    nodos = sorted(G.nodes())
    idx = {n: i for i, n in enumerate(nodos)}
    col = {n: j for j, n in enumerate(nombres)}
    T = X.shape[0]
    W = np.zeros((T, len(nodos), len(nodos)))
    temporales = []
    for u, v in G.edges():
        if u == v:
            continue
        key = next((k for k in (f"{u}-{v}", f"{v}-{u}") if k in col), None)
        if key is None:
            w = np.full(T, peso_estatico)
        else:
            w = X[:, col[key]]
            temporales.append((idx[u], idx[v], col[key]))
        W[:, idx[u], idx[v]] = w
        W[:, idx[v], idx[u]] = w
    sin_casar = len(nombres) - len({c for _, _, c in temporales})
    if sin_casar:
        print(f"AVISO: {sin_casar} series del CSV no casaron con aristas de la red estática")
    return W, nodos, temporales


def refinar_tiempo(W, f):
    """Interpolación lineal periódica de los pesos (f subdivisiones por paso). Igual que el pipeline original."""
    if f <= 1:
        return W
    T = W.shape[0]
    tt = np.arange(T * f) / f
    i0 = np.floor(tt).astype(int) % T
    i1 = (i0 + 1) % T
    a = (tt - np.floor(tt))[:, None, None]
    return (1 - a) * W[i0] + a * W[i1]


def estado_nodos(W, clustering="onnela"):
    """x = log(1 + s), C (Onnela o Barrat con topología fija) y k (grado con w > 0), todos (T, N)."""
    s = W.sum(axis=2)
    k = (W > 0).sum(axis=2)
    if clustering == "barrat":
        A = (W.max(axis=0) > 0).astype(float)
        kA = A.sum(axis=1)
        tri = (W * (A * (A @ A))[None]).sum(axis=2)
        C = np.where(kA > 1, tri / (np.maximum(s, 1e-12) * np.maximum(kA - 1, 1)), 0.0)
    elif clustering == "onnela":
        R = np.cbrt(W / W.max())
        tri = np.einsum("tij,tji->ti", R @ R, R)       # (R^3)_ii, igual que einsum('tij,tjk,tki->ti') pero con BLAS
        den = k * (k - 1)
        C = np.where(den > 0, tri / np.maximum(den, 1), 0.0)
    else:
        raise ValueError(f"clustering desconocido: {clustering!r}")
    return np.log1p(s), C, k


def trayectorias(W, clustering="onnela"):
    """r (T, N, 2) estandarizado sobre todos los nodos y tiempos; también devuelve k."""
    x, C, k = estado_nodos(W, clustering)
    r = np.stack([x, C], axis=-1)
    flat = r.reshape(-1, 2)
    mu, sd = flat.mean(0), flat.std(0)
    return (r - mu) / sd, k
