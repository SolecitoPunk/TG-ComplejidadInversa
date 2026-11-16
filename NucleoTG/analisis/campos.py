"""
campos.py: campos suavizados con kernel gaussiano y derivadas ANALÍTICAS.

Lo comparten todos los bloques del análisis (validación, Phasik, nulos).

Convenciones
------------
- Coordenadas 2D. G: (n, 2) puntos de malla.
- Kernel: K_h(d) = exp(-|d|^2 / 2h^2) / (2 pi h^2).
- Densidad:   P(r) = (1/Np) sum_k K_h(r - a_k)              a_k = muestras de posición
- Corriente:  J(r) = (1/Nj) sum_k K_h(r - b_k) v_k          b_k = punto de anclaje, v_k = velocidad
- Derivadas:  grad K_h(r - c) = -(r - c)/h^2 K_h
              lap  K_h(r - c) = K_h/h^2 (|r - c|^2/h^2 - 2)
              d_b J_a = -(1/(Nj h^2)) sum_k K_h(r - b_k) (r - b_k)_b v_{k,a}
- u = J/P;   d_b u_a = d_b J_a / P - J_a d_b P / P^2   (analítico, sin np.gradient)
- Vorticidad: omega = d_x u_y - d_y u_x.

Esquemas para la corriente (función `muestras`)
-----------------------------------------------
- "adelante" (tipo Itô):          K_h(r - r_k)               (r_{k+1} - r_k)/dt
- "medio"    (tipo Stratonovich): K_h(r - (r_k + r_{k+1})/2) (r_{k+1} - r_k)/dt
Para procesos con ruido, solo "medio" estima la corriente de probabilidad
J = P F - D grad P. "adelante" estima P F (la deriva). Para trayectorias
suaves, ambos convergen a lo mismo cuando dt -> 0, pero "adelante" tiene
error O(dt) en la divergencia y "medio" O(dt^2) o menor.
"""
import numpy as np


def malla(lo, hi, n):
    """Malla regular n x n. Devuelve X, Y (indexing='ij') y G (n*n, 2)."""
    xg = np.linspace(lo[0], hi[0], n)
    yg = np.linspace(lo[1], hi[1], n)
    X, Y = np.meshgrid(xg, yg, indexing="ij")
    return X, Y, np.column_stack([X.ravel(), Y.ravel()])


def muestras(r, dt, esquema="medio", cerrado=True):
    """A partir de trayectorias r (T, N, 2) o (T, 2) devuelve:
      A   : (M, 2) posiciones para la densidad (r_k)
      B   : (M, 2) anclajes de la corriente (según el esquema)
      Vel : (M, 2) velocidades (r_{k+1} - r_k)/dt
    cerrado=True añade el segmento r_{T-1} -> r_0 (trayectoria periódica);
    cerrado=False usa solo los T-1 segmentos internos."""
    r = np.asarray(r, dtype=float)
    if r.ndim == 2:
        r = r[:, None, :]
    if cerrado:
        r0, r1 = r, np.roll(r, -1, axis=0)
    else:
        r0, r1 = r[:-1], r[1:]
    vel = (r1 - r0) / dt
    if esquema == "medio":
        anc = 0.5 * (r0 + r1)
    elif esquema == "adelante":
        anc = r0
    else:
        raise ValueError(f"esquema desconocido: {esquema!r}")
    return r0.reshape(-1, 2), anc.reshape(-1, 2), vel.reshape(-1, 2)


def _bloques(n, m, max_elem):
    c = max(1, int(max_elem // max(m, 1)))
    for a in range(0, n, c):
        yield slice(a, min(n, a + c))


def densidad_kde(G, A, h, max_elem=4e6):
    """P, grad P, lap P en los puntos G a partir de las muestras A."""
    n, Np = len(G), len(A)
    P = np.zeros(n)
    gP = np.zeros((n, 2))
    lP = np.zeros(n)
    norm = 1.0 / (2 * np.pi * h ** 2 * Np)
    for sl in _bloques(n, Np, max_elem):
        d = G[sl, None, :] - A[None, :, :]               # (c, Np, 2)
        q = np.einsum("cnk,cnk->cn", d, d) / h ** 2
        K = np.exp(-0.5 * q)
        P[sl] = K.sum(1) * norm
        gP[sl] = -np.einsum("cn,cnk->ck", K, d) * norm / h ** 2
        lP[sl] = np.einsum("cn,cn->c", K, q - 2.0) * norm / h ** 2
    return P, gP, lP


def corriente_kde(G, B, Vel, h, max_elem=4e6):
    """J y su gradiente gJ[:, a, b] = d_b J_a en los puntos G."""
    n, Nj = len(G), len(B)
    J = np.zeros((n, 2))
    gJ = np.zeros((n, 2, 2))
    norm = 1.0 / (2 * np.pi * h ** 2 * Nj)
    for sl in _bloques(n, Nj, max_elem):
        d = G[sl, None, :] - B[None, :, :]               # (c, Nj, 2)
        K = np.exp(-0.5 * np.einsum("cnk,cnk->cn", d, d) / h ** 2)
        J[sl] = (K @ Vel) * norm
        M = np.swapaxes(K[..., None] * d, 1, 2) @ Vel     # M[c, b, a] = sum_n K d_b v_a
        gJ[sl] = -np.swapaxes(M, 1, 2) * norm / h ** 2
    return J, gJ


def campos_derivados(P, gP, lP, J, gJ):
    """Cantidades derivadas, todas analíticas a partir de las sumas del KDE.
    bohm1 es el término de Bohm por unidad de lambda (= hbar^2/m):
        bohm1 = (1/4) [lap P / P - (1/2) |grad P|^2 / P^2]
    de modo que V = lambda * bohm1 + flujo (+ E constante)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        u = J / P[:, None]
        gu = gJ / P[:, None, None] - J[:, :, None] * gP[:, None, :] / P[:, None, None] ** 2
        g2 = (gP ** 2).sum(1)
        return dict(
            P=P, gP=gP, lP=lP, J=J, gJ=gJ, u=u, gu=gu,
            omega=gu[:, 1, 0] - gu[:, 0, 1],
            divJ=gJ[:, 0, 0] + gJ[:, 1, 1],
            U=-np.log(P),
            lap_lnP=lP / P - g2 / P ** 2,
            bohm1=0.25 * (lP / P - 0.5 * g2 / P ** 2),
            flujo=-0.5 * (u ** 2).sum(1),
        )


def div_relativa(F, mask, h):
    """rms(div J) / (rms|J| / h) en la máscara (misma definición que el pipeline original)."""
    num = np.sqrt(np.mean(F["divJ"][mask] ** 2))
    den = np.sqrt(np.mean((F["J"][mask] ** 2).sum(1))) / h
    return num / den
