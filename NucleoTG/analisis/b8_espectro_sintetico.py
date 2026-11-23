"""
Bloque 8: prueba de viabilidad (sí o no) de la formulación Fokker-Planck / Schrödinger no hermítica.

    python b8_espectro_sintetico.py          # ~3-8 min

Pregunta: con trayectorias sintéticas, ¿el espectro del hamiltoniano reconstruido
    H = -D lap + V_s + (1/2)(v.grad + div(v .)),   V_s = 2D * bohm1   (lambda = 2D)
a partir de (P^, v^, D^) predice la tasa de relajación y la frecuencia que se miden de forma
independiente en la autocorrelación de las trayectorias?

Sistemas:
  OU con rotación   f = -(gamma I + Om Jm) r.  Exacto: lambda_1 = gamma ± i Om.
  Stuart-Landau     dz = [(mu + i w) z - (1 + i beta)|z|^2 z] dt + sqrt(2D) dW  (ciclo límite).
                    Modo de fase: lambda = D_phi ± i w_eff. Referencia de ruido débil (solo orientativa):
                    D_phi ~ D(1 + beta^2)/mu, w_eff ~ w - beta mu.
Verdad numérica: espectro del operador de Fokker-Planck con la deriva VERDADERA en la misma malla.
Observable de la autocorrelación: z = x + iy (OU, autofunción exacta) y z/|z| (SL).

Estimadores:
  D^ : segundas diferencias, <|Δr_{k+1} - Δr_k|^2> / (8 dt)  (cancela la deriva a primer orden)
  P^, grad P^, lap P^, J^ : histograma + filtro gaussiano (y sus derivadas), anchura h
  v^ = J^/P^ con anclaje en el punto medio (bloque 1b)
Malla: Dirichlet fuera de la máscara P^ > EPS * max P^.

Criterios declarados en README_bloque8.md.
"""
import os
import time

import numpy as np
import pandas as pd
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.ndimage import gaussian_filter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
SEED = 7
UMBRAL_OSC = 0.5          # |Im lambda| > 0.5 define un modo oscilatorio


# ============================================================
# Simulación
# ============================================================
def simular_ou(gamma, Om, D, dt, nsteps, ntraj, rng):
    s = D / gamma
    a = np.exp(-gamma * dt)
    c, sn = a * np.cos(-Om * dt), a * np.sin(-Om * dt)
    sd = np.sqrt(s * (1 - a * a))
    r = np.empty((nsteps, ntraj, 2))
    r[0] = rng.normal(0, np.sqrt(s), (ntraj, 2))
    xi = rng.normal(0, sd, (nsteps - 1, ntraj, 2))
    for k in range(nsteps - 1):
        x, y = r[k, :, 0], r[k, :, 1]
        r[k + 1, :, 0] = c * x - sn * y + xi[k, :, 0]
        r[k + 1, :, 1] = sn * x + c * y + xi[k, :, 1]
    return r


def f_ou(x, y, gamma, Om):
    return -gamma * x + Om * y, -Om * x - gamma * y


def f_sl(x, y, mu, w, beta):
    r2 = x * x + y * y
    return mu * x - w * y - r2 * (x - beta * y), w * x + mu * y - r2 * (y + beta * x)


def simular_sl(mu, w, beta, D, dt, nsteps, ntraj, rng, burn=20.0):
    """Heun estocástico (ruido aditivo). Arranca en el ciclo con fase aleatoria y descarta 'burn'."""
    ph = rng.uniform(0, 2 * np.pi, ntraj)
    x, y = np.sqrt(mu) * np.cos(ph), np.sqrt(mu) * np.sin(ph)
    nb = int(burn / dt)
    r = np.empty((nsteps, ntraj, 2))
    amp = np.sqrt(2 * D * dt)
    for k in range(nb + nsteps):
        nx_, ny_ = amp * rng.standard_normal(ntraj), amp * rng.standard_normal(ntraj)
        f0x, f0y = f_sl(x, y, mu, w, beta)
        px, py = x + f0x * dt + nx_, y + f0y * dt + ny_
        f1x, f1y = f_sl(px, py, mu, w, beta)
        x, y = x + 0.5 * (f0x + f1x) * dt + nx_, y + 0.5 * (f0y + f1y) * dt + ny_
        if k >= nb:
            r[k - nb, :, 0], r[k - nb, :, 1] = x, y
    return r


# ============================================================
# Estimación de campos en malla
# ============================================================
def estimar_D(r, dt):
    d = np.diff(r, axis=0)
    dd = np.diff(d, axis=0)
    return float((dd ** 2).sum(-1).mean() / (8 * dt))


def campos_malla(r, dt, L, dx, h):
    edges = np.arange(-L, L + dx / 2, dx)
    c = 0.5 * (edges[1:] + edges[:-1])
    d = np.diff(r, axis=0)
    A = r[:-1].reshape(-1, 2)
    B = (0.5 * (r[:-1] + r[1:])).reshape(-1, 2)
    V = (d / dt).reshape(-1, 2)
    N = len(A)
    HP, _, _ = np.histogram2d(A[:, 0], A[:, 1], bins=[edges, edges])
    HJx, _, _ = np.histogram2d(B[:, 0], B[:, 1], bins=[edges, edges], weights=V[:, 0])
    HJy, _, _ = np.histogram2d(B[:, 0], B[:, 1], bins=[edges, edges], weights=V[:, 1])
    s = h / dx

    def g(Hm, o):
        return gaussian_filter(Hm, s, order=o, mode="constant", truncate=5.0)
    P = g(HP, (0, 0)) / (N * dx ** 2)
    Px = g(HP, (1, 0)) / (N * dx ** 3)
    Py = g(HP, (0, 1)) / (N * dx ** 3)
    lP = (g(HP, (2, 0)) + g(HP, (0, 2))) / (N * dx ** 4)
    Jx = g(HJx, (0, 0)) / (N * dx ** 2)
    Jy = g(HJy, (0, 0)) / (N * dx ** 2)
    # comprobación de signo y escala de las derivadas del filtro frente a diferencias finitas
    gx_fd = np.gradient(P, dx, axis=0)
    w = P > 0.05 * P.max()
    err = np.abs(Px[w] - gx_fd[w]).mean() / np.abs(gx_fd[w]).mean()
    assert err < 0.05, f"derivada del filtro inconsistente (error relativo {err:.3f})"
    with np.errstate(divide="ignore", invalid="ignore"):
        bohm1 = 0.25 * (lP / P - 0.5 * (Px ** 2 + Py ** 2) / P ** 2)
        vx, vy = Jx / P, Jy / P
    X, Y = np.meshgrid(c, c, indexing="ij")
    return dict(X=X, Y=Y, P=P, bohm1=bohm1, vx=vx, vy=vy, N=N)


# ============================================================
# Operadores dispersos (5 puntos, Dirichlet fuera de la máscara)
# ============================================================
def ensamblar(mask, diag, mas, menos):
    """mas[a] / menos[a]: coeficiente hacia el vecino +1 / -1 en el eje a."""
    idx = -np.ones(mask.shape, dtype=np.int64)
    idx[mask] = np.arange(mask.sum())
    rows, cols, vals = [idx[mask]], [idx[mask]], [diag[mask]]
    for a in (0, 1):
        for sgn, coef in ((+1, mas[a]), (-1, menos[a])):
            nb = np.roll(idx, -sgn, axis=a)
            ok = mask & (nb >= 0)
            borde = [slice(None)] * 2
            borde[a] = -1 if sgn == 1 else 0
            ok[tuple(borde)] = False
            rows.append(idx[ok])
            cols.append(nb[ok])
            vals.append(coef[ok])
    n = int(mask.sum())
    return sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))


def H_reconstruido(F, D, dx, eps):
    mask = F["P"] > eps * F["P"].max()
    Vs = 2 * D * F["bohm1"]
    vx, vy = F["vx"], F["vy"]
    k = D / dx ** 2
    mas = [-k + (vx + np.roll(vx, -1, 0)) / (4 * dx), -k + (vy + np.roll(vy, -1, 1)) / (4 * dx)]
    menos = [-k - (vx + np.roll(vx, 1, 0)) / (4 * dx), -k - (vy + np.roll(vy, 1, 1)) / (4 * dx)]
    return ensamblar(mask, 4 * k + Vs, mas, menos), mask


def FP_verdad(X, Y, fx, fy, D, dx):
    """-L P = -D lap P + div(f P), diferencias centrales; caja completa con Dirichlet."""
    k = D / dx ** 2
    mask = np.ones(X.shape, bool)
    mas = [-k + np.roll(fx, -1, 0) / (2 * dx), -k + np.roll(fy, -1, 1) / (2 * dx)]
    menos = [-k - np.roll(fx, 1, 0) / (2 * dx), -k - np.roll(fy, 1, 1) / (2 * dx)]
    return ensamblar(mask, np.full(X.shape, 4 * k), mas, menos)


def espectro(M, k=12, sigma=-0.03):
    vals, vecs = spla.eigs(M.tocsc(), k=k, sigma=sigma, tol=1e-8, maxiter=5000)
    return vals, vecs


def modos(vals):
    i0 = int(np.argmin(np.abs(vals)))
    resto = np.delete(vals, i0)
    osc = resto[np.abs(resto.imag) > UMBRAL_OSC]
    lam_osc = osc[np.argmin(osc.real)] if len(osc) else np.nan
    reales = resto[(np.abs(resto.imag) <= UMBRAL_OSC) & (resto.real > 0)]
    lam_real = reales[np.argmin(reales.real)] if len(reales) else np.nan
    return vals[i0], i0, lam_osc, lam_real


# ============================================================
# Autocorrelación
# ============================================================
def autocorrelacion(g, dt, tau_max):
    T = g.shape[0]
    n = min(int(tau_max / dt), T - 1)
    Fg = np.fft.fft(g, n=2 * T, axis=0)
    R = np.fft.ifft(Fg * np.conj(Fg), axis=0)[:n + 1].mean(1)
    R = R / (T - np.arange(n + 1))
    return np.arange(n + 1) * dt, R / R[0]


def ajustar(tau, C, tau_min, umbral=0.3):
    fin = np.argmax(np.abs(C) < umbral) if np.any(np.abs(C) < umbral) else len(C)
    sel = (tau >= tau_min) & (np.arange(len(C)) < fin)
    a = -np.polyfit(tau[sel], np.log(np.abs(C[sel])), 1)[0]
    b = -np.polyfit(tau[sel], np.unwrap(np.angle(C[sel])), 1)[0]
    return a, abs(b), tau[sel].max() if sel.any() else np.nan


# ============================================================
# Experimentos
# ============================================================
def experimento(nombre, r, dt, L, dx, hs, eps_list, f_true, D_true, obs, tau_min, tau_max, ref):
    filas = []
    X = Y = None
    D_hat = estimar_D(r, dt)
    for frac in (1.0, 0.1):
        rr = r[: max(3, int(frac * r.shape[0]))]
        Dh = estimar_D(rr, dt)
        tau, C = autocorrelacion(obs(rr), dt, tau_max)
        a_ac, b_ac, tfin = ajustar(tau, C, tau_min)
        filas.append(dict(sistema=nombre, fuente="autocorrelación", datos=frac, h=np.nan, eps=np.nan,
                          D_hat=Dh, re=a_ac, im=b_ac, lam0=np.nan, solape0=np.nan, nota=f"ajuste hasta tau={tfin:.1f}"))
        for h in hs:
            F = campos_malla(rr, dt, L, dx, h)
            X, Y = F["X"], F["Y"]
            for eps in eps_list:
                H, mask = H_reconstruido(F, Dh, dx, eps)
                vals, vecs = espectro(H)
                lam0, i0, lo, lr = modos(vals)
                phi0 = np.abs(vecs[:, i0])
                sq = np.sqrt(F["P"][mask])
                sol = float(phi0 @ sq / (np.linalg.norm(phi0) * np.linalg.norm(sq)))
                filas.append(dict(sistema=nombre, fuente="H reconstruido", datos=frac, h=h, eps=eps, D_hat=Dh,
                                  re=lo.real, im=abs(lo.imag), lam0=abs(lam0), solape0=sol,
                                  nota=f"modo real más lento {lr.real:.3g}" if np.isfinite(lr) else ""))
    fx, fy = f_true(X, Y)
    vals, _ = espectro(FP_verdad(X, Y, fx, fy, D_true, dx))
    lam0, _, lo, lr = modos(vals)
    filas.append(dict(sistema=nombre, fuente="FP verdadero (malla)", datos=np.nan, h=np.nan, eps=np.nan,
                      D_hat=D_true, re=lo.real, im=abs(lo.imag), lam0=abs(lam0), solape0=np.nan,
                      nota=f"modo real más lento {lr.real:.3g}" if np.isfinite(lr) else ""))
    filas.append(dict(sistema=nombre, fuente="referencia analítica", datos=np.nan, h=np.nan, eps=np.nan,
                      D_hat=D_true, re=ref[0], im=ref[1], lam0=0.0, solape0=np.nan, nota=ref[2]))
    print(f"  {nombre}: D verdadero {D_true}, D^ (todos los datos) {D_hat:.4g}")
    return filas


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    filas = []

    g_, Om, D = 1.0, 3.0, 0.5
    dt = 0.01
    r = simular_ou(g_, Om, D, dt, nsteps=20000, ntraj=20, rng=rng)
    print(f"OU simulado: {r.shape} ({time.time() - t0:.0f} s)")
    filas += experimento("OU", r, dt, L=3.5, dx=0.05, hs=(0.15, 0.3), eps_list=(1e-4, 1e-6),
                         f_true=lambda X, Y: f_ou(X, Y, g_, Om), D_true=D,
                         obs=lambda rr: rr[..., 0] + 1j * rr[..., 1], tau_min=0.0, tau_max=5.0,
                         ref=(g_, Om, "exacto: gamma ± i Om"))
    print(f"OU listo ({time.time() - t0:.0f} s)")

    mu, w, beta, D = 1.0, 2 * np.pi, 1.0, 0.05
    dt = 0.005
    r = simular_sl(mu, w, beta, D, dt, nsteps=100000, ntraj=20, rng=rng)
    print(f"SL simulado: {r.shape} ({time.time() - t0:.0f} s)")
    filas += experimento("Stuart-Landau", r, dt, L=1.75, dx=0.0125, hs=(0.04, 0.08), eps_list=(1e-4, 1e-6),
                         f_true=lambda X, Y: f_sl(X, Y, mu, w, beta), D_true=D,
                         obs=lambda rr: (rr[..., 0] + 1j * rr[..., 1]) / np.hypot(rr[..., 0], rr[..., 1]),
                         tau_min=1.0, tau_max=60.0,
                         ref=(D * (1 + beta ** 2) / mu, w - beta * mu, "ruido débil, orientativa"))

    df = pd.DataFrame(filas)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "b8_espectro.csv"), index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 20, "display.max_colwidth", 40):
        print("\n=== Primer modo oscilatorio: re = tasa de relajación, im = frecuencia ===")
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print(f"[b8] {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
