"""
Bloque 9: el benchmark Stuart-Landau con violaciones realistas de los supuestos (una a la vez).

    python b9_violaciones.py          # ~6-10 min

Línea base: Stuart-Landau con D constante e isotrópica, trayectorias observadas sin ruido (como b8b).
Violaciones:
  V1  ruido de medición blanco sigma_obs sumado a las trayectorias (0.002, 0.005, 0.01)
  V2  difusión anisotrópica Dx/Dy = q con (Dx + Dy)/2 = D (q = 1.5, 2, 4)
  V3  proyección: se observa solo z1 de un sistema 4D (z1 acoplado a z2 amortiguado, kappa = 0.5, 1, 1.5)
  V4  deriva lenta de mu y omega (amplitud relativa eps = 0.02, 0.05, 0.10; periodo 50 frente a 1.19)

Para cada condición: H reconstruido con h en (0.03, 0.04, 0.06, 0.08), extrapolación a h -> 0 con
re = a0 + c h^2 (b8b), y autocorrelación de z/|z| como medida independiente. Estadísticos:
  err_ref : re_a0 / re_verdadero - 1        (solo si hay verdad: V1, V2, V4 usa el sistema sin deriva)
  disc    : re_a0 / re_ac - 1               (chequeo de consistencia; usa solo los datos)
  resid_h2: residuo relativo del ajuste en h^2 (segundo detector posible)
Criterios y predicciones: README_bloque9.md (declarados antes de ejecutar).

D se estima de dos formas:
  std : <|r_{k+2} - 2 r_{k+1} + r_k|^2> / (8 dt)                (b8; sensible al ruido de medición)
  rob : pendiente de var_dd(m) = 8 D (m dt) + 12 sigma^2 para m = 1..4   (la ordenada da sigma^2)
"""
import os
import time

import numpy as np
import pandas as pd

import b8_espectro_sintetico as b8
import b8b_seguimiento as b8b

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
MU, W, BETA, D, DT = b8b.MU, b8b.W, b8b.BETA, b8b.D, b8b.DT
L, DX, EPS = b8b.L, b8b.DX, b8b.EPS
NSTEPS, NTRAJ = 40000, 20
SEEDS = (21, 22, 23)
HS9 = (0.03, 0.04, 0.06, 0.08)
UMBRAL_FLAG = 0.25
RUIDOS = (0.002, 0.005, 0.01)
ANISO = (1.5, 2.0, 4.0)
KAPPAS = (0.5, 1.0, 1.5)
DRIFTS = (0.02, 0.05, 0.10)
GAM2, W2, D2 = 2.0, 3.0, D          # oscilador auxiliar del sistema 4D


# ============================================================
# Simuladores
# ============================================================
def simular_sl_gen(rng, Dx=D, Dy=D, eps=0.0, T_slow=50.0, burn=20.0):
    """Stuart-Landau con Heun, ruido aditivo (Dx, Dy) y deriva lenta
    mu(t) = MU (1 + eps sin(2 pi t/T_slow + phi_i)), w(t) igual con otra fase. Fases al azar por trayectoria."""
    ph = rng.uniform(0, 2 * np.pi, NTRAJ)
    x, y = np.sqrt(MU) * np.cos(ph), np.sqrt(MU) * np.sin(ph)
    p_mu, p_w = rng.uniform(0, 2 * np.pi, NTRAJ), rng.uniform(0, 2 * np.pi, NTRAJ)
    nb = int(burn / DT)
    ax, ay = np.sqrt(2 * Dx * DT), np.sqrt(2 * Dy * DT)
    r = np.empty((NSTEPS, NTRAJ, 2))

    def par(t):
        return (MU * (1 + eps * np.sin(2 * np.pi * t / T_slow + p_mu)),
                W * (1 + eps * np.sin(2 * np.pi * t / T_slow + p_w)))
    for k in range(nb + NSTEPS):
        t = (k - nb) * DT
        m0, w0 = par(t)
        m1, w1 = par(t + DT)
        nx_, ny_ = ax * rng.standard_normal(NTRAJ), ay * rng.standard_normal(NTRAJ)
        f0x, f0y = b8.f_sl(x, y, m0, w0, BETA)
        px, py = x + f0x * DT + nx_, y + f0y * DT + ny_
        f1x, f1y = b8.f_sl(px, py, m1, w1, BETA)
        x, y = x + 0.5 * (f0x + f1x) * DT + nx_, y + 0.5 * (f0y + f1y) * DT + ny_
        if k >= nb:
            r[k - nb, :, 0], r[k - nb, :, 1] = x, y
    return r


def simular_sl4d(rng, kappa, burn=20.0):
    """z1 = (x, y): Stuart-Landau. z2 = (u, v): dz2 = [(-GAM2 + i W2) z2 + kappa z1] dt + ruido D2.
    dz1 = [SL(z1) + kappa z2] dt + ruido D. Solo se devuelve z1."""
    ph = rng.uniform(0, 2 * np.pi, NTRAJ)
    x, y = np.sqrt(MU) * np.cos(ph), np.sqrt(MU) * np.sin(ph)
    u, v = np.zeros(NTRAJ), np.zeros(NTRAJ)
    nb = int(burn / DT)
    a1, a2 = np.sqrt(2 * D * DT), np.sqrt(2 * D2 * DT)
    r = np.empty((NSTEPS, NTRAJ, 2))

    def drift(x, y, u, v):
        fx, fy = b8.f_sl(x, y, MU, W, BETA)
        return (fx + kappa * u, fy + kappa * v,
                -GAM2 * u - W2 * v + kappa * x, W2 * u - GAM2 * v + kappa * y)
    for k in range(nb + NSTEPS):
        n = [a * rng.standard_normal(NTRAJ) for a in (a1, a1, a2, a2)]
        d0 = drift(x, y, u, v)
        pp = (x + d0[0] * DT + n[0], y + d0[1] * DT + n[1], u + d0[2] * DT + n[2], v + d0[3] * DT + n[3])
        d1 = drift(*pp)
        x, y, u, v = (x + 0.5 * (d0[0] + d1[0]) * DT + n[0], y + 0.5 * (d0[1] + d1[1]) * DT + n[1],
                      u + 0.5 * (d0[2] + d1[2]) * DT + n[2], v + 0.5 * (d0[3] + d1[3]) * DT + n[3])
        if k >= nb:
            r[k - nb, :, 0], r[k - nb, :, 1] = x, y
    return r


# ============================================================
# Estimadores de D
# ============================================================
def estimar_D_robusto(r, dt, ms=(1, 2, 3, 4)):
    """Ajuste lineal de var_dd(m) = 8 D (m dt) + 12 sigma^2. Devuelve (D, sigma_obs^2)."""
    x, v = [], []
    for m in ms:
        dd = r[2 * m:] - 2 * r[m:-m] + r[:-2 * m]
        v.append((dd ** 2).sum(-1).mean())
        x.append(m * dt)
    b, a = np.polyfit(x, v, 1)
    return b / 8.0, max(a, 0.0) / 12.0


def estimar_D_ejes(r, dt):
    dd = r[2:] - 2 * r[1:-1] + r[:-2]
    return (dd[..., 0] ** 2).mean() / (4 * dt), (dd[..., 1] ** 2).mean() / (4 * dt)


# ============================================================
# Referencias
# ============================================================
def fp_aniso(X, Y, fx, fy, Dx, Dy, dx):
    k0, k1 = Dx / dx ** 2, Dy / dx ** 2
    mas = [-k0 + np.roll(fx, -1, 0) / (2 * dx), -k1 + np.roll(fy, -1, 1) / (2 * dx)]
    menos = [-k0 - np.roll(fx, 1, 0) / (2 * dx), -k1 - np.roll(fy, 1, 1) / (2 * dx)]
    return b8.ensamblar(np.ones(X.shape, bool), np.full(X.shape, 2 * k0 + 2 * k1), mas, menos)


def referencia(Dx=D, Dy=D):
    X, Y = b8b.malla_centros(L, DX)
    fx, fy = b8.f_sl(X, Y, MU, W, BETA)
    return b8b.modo(fp_aniso(X, Y, fx, fy, Dx, Dy, DX))


# ============================================================
# Evaluación de una condición
# ============================================================
def ac_seguro(r, dt):
    obs = (r[..., 0] + 1j * r[..., 1]) / np.hypot(r[..., 0], r[..., 1])
    try:
        tau, C = b8.autocorrelacion(obs, dt, 60.0)
        a, b, _ = b8.ajustar(tau, C, 1.0)
        return a, b
    except Exception as e:
        print(f"    aviso: ajuste de la autocorrelación fallido ({type(e).__name__})")
        return np.nan, np.nan


def evaluar(r, dt, variantes=("std",)):
    re_ac, im_ac = ac_seguro(r, dt)
    D_std = b8.estimar_D(r, dt)
    D_rob, s2 = estimar_D_robusto(r, dt)
    dx_hat, dy_hat = estimar_D_ejes(r, dt)
    Dv = {"std": D_std, "rob": D_rob}
    Fs = {h: b8.campos_malla(r, dt, L, DX, h) for h in HS9}
    filas = []
    for var in variantes:
        res = [b8b.modo(b8.H_reconstruido(Fs[h], Dv[var], DX, EPS)[0]) for h in HS9]
        re_h = np.array([x[0] for x in res])
        im_h = np.array([x[1] for x in res])
        if np.all(np.isfinite(re_h)):
            c, a0 = np.polyfit(np.array(HS9) ** 2, re_h, 1)
            resid = np.sqrt(np.mean((re_h - (a0 + c * np.array(HS9) ** 2)) ** 2)) / re_h.mean()
        else:
            a0, resid = np.nan, np.nan
        filas.append(dict(variante_D=var, D_hat=Dv[var], D_std=D_std, D_rob=D_rob, s_obs_hat=np.sqrt(s2),
                          ratio_ejes_hat=dx_hat / dy_hat, re_a0=a0, re_h04=re_h[1], im_h04=im_h[1],
                          resid_h2=resid, re_ac=re_ac, im_ac=im_ac))
    return filas


# ============================================================
# Programa principal
# ============================================================
def main():
    t0 = time.time()
    ref_iso = referencia()
    ref_aniso = {q: referencia(2 * D * q / (1 + q), 2 * D / (1 + q)) for q in ANISO}
    print(f"Referencia isotrópica: re = {ref_iso[0]:.4f}, im = {ref_iso[1]:.4f}")
    for q, v in ref_aniso.items():
        print(f"Referencia anisotrópica q = {q}: re = {v[0]:.4f}, im = {v[1]:.4f}")

    filas = []

    def anotar(violacion, nivel, seed, evals, ref):
        for f in evals:
            filas.append(dict(violacion=violacion, nivel=nivel, seed=seed, ref_re=ref[0], ref_im=ref[1], **f))

    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        r0 = simular_sl_gen(rng)
        anotar("base", 0.0, seed, evaluar(r0, DT, ("std", "rob")), ref_iso)
        for s in RUIDOS:
            rn = r0 + s * np.random.default_rng(1000 * seed + int(s * 1e4)).standard_normal(r0.shape)
            anotar("V1 ruido", s, seed, evaluar(rn, DT, ("std", "rob")), ref_iso)
        for q in ANISO:
            ra = simular_sl_gen(np.random.default_rng(100 * seed + int(10 * q)),
                                Dx=2 * D * q / (1 + q), Dy=2 * D / (1 + q))
            anotar("V2 aniso", q, seed, evaluar(ra, DT), ref_aniso[q])
        for kap in KAPPAS:
            rp = simular_sl4d(np.random.default_rng(100 * seed + int(10 * kap)), kap)
            anotar("V3 proyección", kap, seed, evaluar(rp, DT), (np.nan, np.nan))
        for e in DRIFTS:
            rd = simular_sl_gen(np.random.default_rng(100 * seed + int(100 * e)), eps=e)
            anotar("V4 deriva", e, seed, evaluar(rd, DT), ref_iso)
        print(f"  semilla {seed}: {time.time() - t0:.0f} s acumulados")

    df = pd.DataFrame(filas)
    df["err_ref"] = df.re_a0 / df.ref_re - 1
    df["err_im"] = df.im_h04 / df.ref_im - 1
    df["disc"] = df.re_a0 / df.re_ac - 1
    df["flag"] = df.disc.abs() > UMBRAL_FLAG
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "b9_resultados.csv"), index=False)

    tab = df.groupby(["violacion", "nivel", "variante_D"], sort=False).agg(
        D_hat=("D_hat", "mean"), D_rob=("D_rob", "mean"), s_obs_hat=("s_obs_hat", "mean"),
        ratio_ejes=("ratio_ejes_hat", "mean"), re_a0=("re_a0", "mean"), re_ac=("re_ac", "mean"),
        err_ref=("err_ref", "mean"), err_im=("err_im", "mean"), disc=("disc", "mean"),
        disc_abs=("disc", lambda s: s.abs().mean()), flag=("flag", "mean"), resid_h2=("resid_h2", "mean")
    ).reset_index()
    with pd.option_context("display.width", 280, "display.max_columns", 30):
        print("\n=== Resumen (medias de 3 semillas) ===")
        print(tab.to_string(index=False, float_format=lambda v: f"{v:.4g}"))

    # ---- criterios declarados (README_bloque9.md) ----
    def ver(nombre, ok, detalle):
        print(f"  [{'CUMPLE' if ok else 'NO CUMPLE'}] {nombre}: {detalle}")
    print("\n=== Criterios declarados ===")
    b = df[(df.violacion == "base") & (df.variante_D == "std")]
    ver("B0 línea base", bool((b.err_ref.abs() <= 0.10).all() and (b.disc.abs() <= UMBRAL_FLAG).all()
                              and (b.err_im.abs() <= 0.05).all()),
        f"err_ref {b.err_ref.round(3).tolist()}, disc {b.disc.round(3).tolist()}")
    n = df[(df.violacion == "V1 ruido") & (df.variante_D == "std")].groupby("nivel").mean(numeric_only=True)
    pred = 1.5 * n.index.values ** 2 / (D * DT)
    obs = n.D_std.values / D - 1
    ver("V1a D estándar sigue 1.5 s^2/(D dt)", bool(np.all(np.abs(obs - pred) <= 0.05)),
        f"observado {np.round(obs, 3).tolist()} predicho {np.round(pred, 3).tolist()}")
    ver("V1b D robusto dentro del 10 %", bool(np.all(np.abs(n.D_rob.values / D - 1) <= 0.10)),
        f"error {np.round(n.D_rob.values / D - 1, 3).tolist()}")
    r_ = df[(df.violacion == "V1 ruido") & (df.variante_D == "rob") & (df.nivel <= 0.005)].groupby("nivel").err_ref.mean()
    ver("V1c con D robusto, |err_ref| <= 0.30 si sigma <= 0.005", bool((r_.abs() <= 0.30).all()),
        f"err_ref {np.round(r_.values, 3).tolist()}")
    a = df[df.violacion == "V2 aniso"].groupby("nivel").ratio_ejes_hat.mean()
    ver("V2a anisotropía detectable (±10 %)", bool(np.all(np.abs(a.values / a.index.values - 1) <= 0.10)),
        f"estimado {np.round(a.values, 3).tolist()} para q = {list(a.index)}")
    p = df[df.violacion == "V3 proyección"].groupby("nivel").disc.apply(lambda s: s.abs().mean())
    ver("V3 el chequeo detecta la memoria (|disc| > 0.25 con kappa = 1.5)", bool(p.iloc[-1] > UMBRAL_FLAG),
        f"|disc| {np.round(p.values, 3).tolist()} para kappa = {list(p.index)}")
    d = df[df.violacion == "V4 deriva"].groupby("nivel").disc.apply(lambda s: s.abs().mean())
    ver("V4 el chequeo detecta la deriva (|disc| > 0.25 con eps = 0.10)", bool(d.iloc[-1] > UMBRAL_FLAG),
        f"|disc| {np.round(d.values, 3).tolist()} para eps = {list(d.index)}")
    print(f"[b9] {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
