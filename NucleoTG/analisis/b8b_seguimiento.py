"""
Bloque 8b: seguimiento de la prueba de viabilidad (b8).

    python b8b_seguimiento.py          # ~3-6 min

1. Control con campos EXACTOS (sin datos): P, bohm1 y v analíticos en la malla, ensamblados con la
   misma H_reconstruido. Separa el error de ensamblado del sesgo de estimación.
     OU:  U = r^2/(2s), s = D/gamma;  v = (Om y, -Om x)
     SL:  U = (r^4/4 - mu r^2/2)/D;   v = (w - beta r^2)(-y, x)
          (la parte radial de la deriva es un gradiente y la tangencial es solenoidal y ortogonal
           a grad U, así que P_s = exp(-U) exacta)
     bohm1 = (1/4)(|grad U|^2/2 - lap U), igual que (1/4)[lapP/P - |grad P|^2/(2P^2)] con P = e^{-U}.
2. Barrido de h y de fracción de datos con varias semillas (solo Stuart-Landau).
3. Ajuste lineal re(h) = a0 + c h^2 sobre las medias con todos los datos.
Criterios en README_bloque8b.md (declarados antes de ejecutar).
"""
import os
import time

import numpy as np
import pandas as pd

import b8_espectro_sintetico as b8

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
MU, W, BETA, D = 1.0, 2 * np.pi, 1.0, 0.05
DT = 0.005
L, DX = 1.75, 0.0125
NSTEPS, NTRAJ = 100000, 20
HS = (0.03, 0.04, 0.06, 0.08)
FRACS = (1.0, 0.1, 0.03, 0.01)
SEEDS = (11, 12, 13, 14, 15)
EPS = 1e-4
TOL_RE, TOL_IM = 0.30, 0.05


def malla_centros(L_, dx):
    edges = np.arange(-L_, L_ + dx / 2, dx)
    c = 0.5 * (edges[1:] + edges[:-1])
    return np.meshgrid(c, c, indexing="ij")


def campos_exactos(sistema, L_, dx, D_, **p):
    X, Y = malla_centros(L_, dx)
    r2 = X ** 2 + Y ** 2
    if sistema == "OU":
        s = D_ / p["gamma"]
        U = r2 / (2 * s)
        gU2 = r2 / s ** 2
        lU = np.full_like(X, 2 / s)
        vx, vy = p["Om"] * Y, -p["Om"] * X
    else:
        mu, w, beta = p["mu"], p["w"], p["beta"]
        U = (r2 ** 2 / 4 - mu * r2 / 2) / D_
        gU2 = r2 * (r2 - mu) ** 2 / D_ ** 2
        lU = (4 * r2 - 2 * mu) / D_
        vx, vy = -(w - beta * r2) * Y, (w - beta * r2) * X
    return dict(X=X, Y=Y, P=np.exp(-(U - U.min())), bohm1=0.25 * (0.5 * gU2 - lU), vx=vx, vy=vy)


def modo(M):
    try:
        vals, _ = b8.espectro(M)
        _, _, lo, _ = b8.modos(vals)
        return lo.real, abs(lo.imag)
    except Exception as e:                      # ARPACK sin convergencia con datos muy escasos
        print(f"    aviso: espectro no calculado ({type(e).__name__})")
        return np.nan, np.nan


def control_exacto():
    print("=== 1. Control con campos exactos ===")
    casos = [("OU", dict(gamma=1.0, Om=3.0), 0.5, 3.5, 0.05, lambda X, Y: b8.f_ou(X, Y, 1.0, 3.0)),
             ("Stuart-Landau", dict(mu=MU, w=W, beta=BETA), D, L, DX, lambda X, Y: b8.f_sl(X, Y, MU, W, BETA))]
    filas = []
    for nombre, p, D_, L_, dx, f in casos:
        F = campos_exactos("OU" if nombre == "OU" else "SL", L_, dx, D_, **p)
        H, _ = b8.H_reconstruido(F, D_, dx, EPS)
        re, im = modo(H)
        fx, fy = f(F["X"], F["Y"])
        re0, im0 = modo(b8.FP_verdad(F["X"], F["Y"], fx, fy, D_, dx))
        filas.append(dict(sistema=nombre, re_exacto=re, im_exacto=im, re_FP=re0, im_FP=im0,
                          err_re=re / re0 - 1, err_im=im / im0 - 1))
    df = pd.DataFrame(filas)
    print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    return df


def barrido():
    print("\n=== 2. Barrido de h, datos y semillas (Stuart-Landau) ===")
    F0 = campos_exactos("SL", L, DX, D, mu=MU, w=W, beta=BETA)
    fx, fy = b8.f_sl(F0["X"], F0["Y"], MU, W, BETA)
    ref_re, ref_im = modo(b8.FP_verdad(F0["X"], F0["Y"], fx, fy, D, DX))
    print(f"Referencia (FP verdadero en la malla): re = {ref_re:.4f}, im = {ref_im:.4f}")
    filas = []
    for seed in SEEDS:
        t0 = time.time()
        r = b8.simular_sl(MU, W, BETA, D, DT, NSTEPS, NTRAJ, np.random.default_rng(seed))
        for frac in FRACS:
            rr = r[: max(3, int(frac * r.shape[0]))]
            Dh = b8.estimar_D(rr, DT)
            for h in HS:
                F = b8.campos_malla(rr, DT, L, DX, h)
                H, _ = b8.H_reconstruido(F, Dh, DX, EPS)
                re, im = modo(H)
                filas.append(dict(seed=seed, datos=frac, h=h, D_hat=Dh, re=re, im=im))
        print(f"  semilla {seed}: {time.time() - t0:.0f} s")
    df = pd.DataFrame(filas)
    df["ok"] = (np.abs(df.re / ref_re - 1) <= TOL_RE) & (np.abs(df.im / ref_im - 1) <= TOL_IM)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "b8b_barrido.csv"), index=False)

    ciclos = NSTEPS * DT * NTRAJ * ref_im / (2 * np.pi)
    tab = df.groupby(["datos", "h"]).agg(re_media=("re", "mean"), re_sd=("re", "std"),
                                         im_media=("im", "mean"), im_sd=("im", "std"),
                                         D_hat=("D_hat", "mean"), frac_ok=("ok", "mean")).reset_index()
    tab["err_re_pct"] = 100 * (tab.re_media / ref_re - 1)
    tab["err_im_pct"] = 100 * (tab.im_media / ref_im - 1)
    tab.insert(1, "ciclos", tab.datos * ciclos)
    print(f"\nCriterio por semilla: |re/ref - 1| <= {TOL_RE}, |im/ref - 1| <= {TOL_IM}. "
          f"frac_ok = fracción de las {len(SEEDS)} semillas que lo cumple.")
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    tab.to_csv(os.path.join(OUT, "b8b_resumen.csv"), index=False)

    print("\n=== 3. Ajuste re(h) = a0 + c h^2 (todos los datos, medias entre semillas) ===")
    m = df[df.datos == 1.0].groupby("h").re.mean()
    h2 = m.index.values ** 2
    c, a0 = np.polyfit(h2, m.values, 1)
    resid = np.sqrt(np.mean((m.values - (a0 + c * h2)) ** 2)) / m.values.mean()
    print(f"a0 = {a0:.4f} ({100 * (a0 / ref_re - 1):+.1f} % frente a la referencia), c = {c:.2f}, "
          f"residuo relativo = {100 * resid:.1f} %")


if __name__ == "__main__":
    t0 = time.time()
    control_exacto()
    barrido()
    print(f"[b8b] {time.time() - t0:.0f} s")
