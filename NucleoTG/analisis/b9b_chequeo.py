"""
Bloque 9b: chequeo de consistencia con intervalo de confianza propio, calibración y ruido mayor.

    python b9b_chequeo.py          # ~12-20 min

1. Chequeo: la tasa de relajación de H (a0, extrapolada a h -> 0) se compara con el intervalo del 95 %
   de la tasa de la autocorrelación de z/|z|, obtenido por remuestreo de trayectorias (B = 500).
   Ventana del ajuste fija a partir de los datos completos: tau en [TAU_MIN, primer |C| < 0.3].
   Bandera = a0 fuera del intervalo. Si la ventana dura < 1 unidad de tiempo, la bandera se activa
   (los datos se decorrelacionan antes de que se separen los modos rápidos).
2. Tasa de falsos positivos: línea base con 20 semillas.
3. Potencia: V4 (deriva, eps = 0.02 y 0.05) y V3 (proyección, kappa = 1.0 y 1.5), 10 semillas cada uno.
4. Ruido de medición mayor (sigma = 0.02, 0.05, 0.1) sobre 5 trayectorias de la línea base, con D_rob,
   y corrección a0_corr = a0 - c_fit * sigma_hat^2 (ancho efectivo h_ef^2 = h^2 + sigma^2).
5. Comprobación del supuesto: dispersión de H por remuestreo (B_H = 10, h = 0.04) frente a la de la
   autocorrelación, en 3 semillas de la línea base.
Criterios en README_bloque9b.md (declarados antes de ejecutar).
"""
import os
import time

import numpy as np
import pandas as pd

import b8_espectro_sintetico as b8
import b8b_seguimiento as b8b
import b9_violaciones as b9

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
DT, L, DX, EPS = b9.DT, b9.L, b9.DX, b9.EPS
HS = b9.HS9
TAU_MIN, TAU_MIN_ALT, UMBRAL_C, TAU_MAX = 3.0, 1.0, 0.3, 60.0
B_AC, B_H = 500, 10
C_B8B, REF_RE = 13.57, 0.1065
SEEDS_BASE = tuple(range(100, 120))
SEEDS_POT = tuple(range(200, 210))
SIGMAS = (0.02, 0.05, 0.1)
N_RUIDO = 5
N_HBOOT = 3


# ============================================================
# Autocorrelación por trayectoria e intervalo por remuestreo
# ============================================================
def ac_por_trayectoria(r, dt, tau_max=TAU_MAX):
    g = (r[..., 0] + 1j * r[..., 1]) / np.hypot(r[..., 0], r[..., 1])
    T = g.shape[0]
    n = min(int(tau_max / dt), T - 1)
    Fg = np.fft.fft(g, n=2 * T, axis=0)
    R = np.fft.ifft(Fg * np.conj(Fg), axis=0)[:n + 1] / (T - np.arange(n + 1))[:, None]
    return np.arange(n + 1) * dt, R                      # R: (n+1, M)


def ventana(tau, C, tau_min):
    absC = np.abs(C)
    fin = int(np.argmax(absC < UMBRAL_C)) if np.any(absC < UMBRAL_C) else len(C)
    sel = (tau >= tau_min) & (np.arange(len(C)) < fin)
    return sel


def tasa(tau, C, sel):
    return -np.polyfit(tau[sel], np.log(np.abs(C[sel])), 1)[0]


def chequeo_ac(r, dt, rng, tau_min=TAU_MIN):
    tau, R = ac_por_trayectoria(r, dt)
    Rm = R.mean(1)
    C = Rm / Rm[0]
    sel = ventana(tau, C, tau_min)
    dur = tau[sel].max() - tau[sel].min() if sel.sum() > 1 else 0.0
    if dur < 1.0:
        return dict(re_ac=np.nan, ic_lo=np.nan, ic_hi=np.nan, se_ac=np.nan, ventana=dur)
    re = tasa(tau, C, sel)
    M = R.shape[1]
    boot = np.empty(B_AC)
    for b in range(B_AC):
        Rb = R[:, rng.integers(M, size=M)].mean(1)
        boot[b] = tasa(tau, Rb / Rb[0], sel)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return dict(re_ac=re, ic_lo=lo, ic_hi=hi, se_ac=boot.std(), ventana=dur)


# ============================================================
# Hamiltoniano reconstruido con extrapolación en h^2
# ============================================================
def eval_H(r, dt, D_val, hs=HS):
    re_h, im_h = [], []
    for h in hs:
        F = b8.campos_malla(r, dt, L, DX, h)
        re, im = b8b.modo(b8.H_reconstruido(F, D_val, DX, EPS)[0])
        re_h.append(re)
        im_h.append(im)
    re_h, im_h = np.array(re_h), np.array(im_h)
    if len(hs) > 1 and np.all(np.isfinite(re_h)):
        c, a0 = np.polyfit(np.array(hs) ** 2, re_h, 1)
    else:
        c, a0 = np.nan, re_h[0]
    return dict(a0=a0, c_fit=c, im_h=im_h[min(1, len(hs) - 1)])


def fila(cond, nivel, seed, r, rng, D_val=None, sigma_hat=0.0, extra=None):
    D_val = b8.estimar_D(r, DT) if D_val is None else D_val
    H = eval_H(r, DT, D_val)
    A = chequeo_ac(r, DT, rng, TAU_MIN)
    A1 = chequeo_ac(r, DT, rng, TAU_MIN_ALT)
    a0c = H["a0"] - H["c_fit"] * sigma_hat ** 2
    out = dict(condicion=cond, nivel=nivel, seed=seed, D=D_val, sigma_hat=sigma_hat, **H, a0_corr=a0c,
               re_ac=A["re_ac"], ic_lo=A["ic_lo"], ic_hi=A["ic_hi"], se_ac=A["se_ac"], ventana=A["ventana"],
               re_ac_t1=A1["re_ac"], ic_lo_t1=A1["ic_lo"], ic_hi_t1=A1["ic_hi"])
    for k, a in (("", a0c), ("_t1", a0c)):
        lo, hi = out[f"ic_lo{k}"], out[f"ic_hi{k}"]
        out[f"flag{k}"] = bool(not np.isfinite(lo) or a < lo or a > hi)
    if extra:
        out.update(extra)
    return out


# ============================================================
# Programa principal
# ============================================================
def main():
    t0 = time.time()
    filas, guardadas = [], []

    print("=== 2. Línea base (falsos positivos) ===")
    for i, s in enumerate(SEEDS_BASE):
        rng = np.random.default_rng(s)
        r = b9.simular_sl_gen(rng)
        filas.append(fila("base", 0.0, s, r, np.random.default_rng(s + 7)))
        if i < max(N_RUIDO, N_HBOOT):
            guardadas.append((s, r))
    print(f"  {time.time() - t0:.0f} s")

    print("=== 3. Potencia ===")
    for e in (0.02, 0.05):
        for s in SEEDS_POT:
            r = b9.simular_sl_gen(np.random.default_rng(s + int(1000 * e)), eps=e)
            filas.append(fila("V4 deriva", e, s, r, np.random.default_rng(s + 11)))
    for kap in (1.0, 1.5):
        for s in SEEDS_POT:
            r = b9.simular_sl4d(np.random.default_rng(s + int(100 * kap)), kap)
            filas.append(fila("V3 proyección", kap, s, r, np.random.default_rng(s + 13)))
    print(f"  {time.time() - t0:.0f} s")

    print("=== 4. Ruido de medición mayor ===")
    for s, r0 in guardadas[:N_RUIDO]:
        for sig in SIGMAS:
            rn = r0 + sig * np.random.default_rng(s * 31 + int(1e3 * sig)).standard_normal(r0.shape)
            Drob, s2 = b9.estimar_D_robusto(rn, DT)
            filas.append(fila("V1 ruido (D_rob)", sig, s, rn, np.random.default_rng(s + 17),
                              D_val=Drob, sigma_hat=np.sqrt(s2)))
            filas.append(fila("V1 ruido (D_std)", sig, s, rn, np.random.default_rng(s + 19), sigma_hat=0.0))
    print(f"  {time.time() - t0:.0f} s")

    print("=== 5. Dispersión de H por remuestreo ===")
    hb = []
    for s, r0 in guardadas[:N_HBOOT]:
        rng = np.random.default_rng(s + 23)
        Dh = b8.estimar_D(r0, DT)
        vals = [eval_H(r0[:, rng.integers(r0.shape[1], size=r0.shape[1])], DT, Dh, hs=(0.04,))["a0"]
                for _ in range(B_H)]
        se_ac = next(f["se_ac"] for f in filas if f["condicion"] == "base" and f["seed"] == s)
        hb.append(dict(seed=s, sd_H=np.std(vals, ddof=1), se_ac=se_ac, razon=np.std(vals, ddof=1) / se_ac))
    dhb = pd.DataFrame(hb)
    print(dhb.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print(f"  {time.time() - t0:.0f} s")

    df = pd.DataFrame(filas)
    df["err_ref"] = df.a0 / REF_RE - 1
    df["err_ref_corr"] = df.a0_corr / REF_RE - 1
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, "b9b_resultados.csv"), index=False)
    dhb.to_csv(os.path.join(OUT, "b9b_hboot.csv"), index=False)

    tab = df.groupby(["condicion", "nivel"], sort=False).agg(
        n=("seed", "size"), a0=("a0", "mean"), a0_corr=("a0_corr", "mean"), re_ac=("re_ac", "mean"),
        se_ac=("se_ac", "mean"), ventana=("ventana", "mean"), err_ref=("err_ref", "mean"),
        err_ref_corr=("err_ref_corr", "mean"), sigma_hat=("sigma_hat", "mean"),
        flag=("flag", "mean"), flag_t1=("flag_t1", "mean")).reset_index()
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print("\n=== Resumen ===")
        print(tab.to_string(index=False, float_format=lambda v: f"{v:.4g}"))

    def ver(nombre, ok, detalle):
        print(f"  [{'CUMPLE' if ok else 'NO CUMPLE'}] {nombre}: {detalle}")
    print("\n=== Criterios declarados ===")
    fr = df[df.condicion == "base"].flag.mean()
    ver("C1 falsos positivos <= 0.10 (tau_min = 3)", fr <= 0.10,
        f"{fr:.2f} ({int(df[df.condicion == 'base'].flag.sum())}/{len(SEEDS_BASE)}); con tau_min = 1: "
        f"{df[df.condicion == 'base'].flag_t1.mean():.2f}")
    p4 = df[(df.condicion == "V4 deriva") & (df.nivel == 0.05)].flag.mean()
    ver("C2 potencia V4 eps = 0.05 >= 0.8", p4 >= 0.8, f"{p4:.2f}")
    p3 = df[(df.condicion == "V3 proyección") & (df.nivel == 1.5)].flag.mean()
    ver("C3 potencia V3 kappa = 1.5 >= 0.8", p3 >= 0.8, f"{p3:.2f}")
    rr = df[df.condicion == "V1 ruido (D_rob)"].groupby("nivel").mean(numeric_only=True)
    pred = C_B8B * rr.index.values ** 2 / REF_RE
    obs = rr.err_ref.values
    m = rr.index.values <= 0.05
    ver("C4 sesgo sin corregir = 13.57 sigma^2 / ref (±30 %), sigma <= 0.05",
        bool(np.all(np.abs(obs[m] / pred[m] - 1) <= 0.30)),
        f"observado {np.round(obs, 3).tolist()} predicho {np.round(pred, 3).tolist()} (sigma = {list(rr.index)})")
    ver("C5 corregido |err_ref_corr| <= 0.10, sigma <= 0.05", bool(np.all(np.abs(rr.err_ref_corr.values[m]) <= 0.10)),
        f"{np.round(rr.err_ref_corr.values, 3).tolist()}")
    ver("C6 dispersión de H <= 0.5 de la de la autocorrelación", bool((dhb.razon <= 0.5).all()),
        f"razón {np.round(dhb.razon.values, 3).tolist()}")
    print(f"[b9b] {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
