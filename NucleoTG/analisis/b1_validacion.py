"""
Bloque 1: pruebas con solución conocida (validación del pipeline).

    python b1_validacion.py          # las tres pruebas
    python b1_validacion.py 1a       # solo una (1a, 1b o 1c)

Imprime tablas y las guarda en resultados/b1_*.csv. Semillas fijas.
Las predicciones (qué apoya y qué refuta cada prueba) están en README_bloque1.md.

Convención de rotación: Jm = [[0, -1], [1, 0]], es decir Jm (x, y) = (-y, x),
y R(theta) = exp(theta Jm) es antihoraria. Para cualquier campo a,
rot(Jm a) = div(a); por eso el campo Omega Jm r tiene vorticidad +2 Omega.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

from campos import (malla, muestras, densidad_kde, corriente_kde,
                    campos_derivados, div_relativa)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
MASK_FRAC = 0.05


def _guardar(df, nombre):
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, nombre), index=False)
    with pd.option_context("display.width", 200, "display.max_columns", 30):
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


# ============================================================
# 1a. Rotación rígida
# ============================================================
def rotacion_rigida(N, T, sigma, seed):
    """N puntos gaussianos (varianza sigma^2 por eje) que giran una vuelta en t in [0, 1).
    Trayectorias cerradas: r(T) = r(0)."""
    rng = np.random.default_rng(seed)
    r0 = rng.normal(0.0, sigma, (N, 2))
    Om = 2 * np.pi
    dt = 1.0 / T
    ang = Om * np.arange(T) * dt
    c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
    r = np.stack([c * r0[:, 0] - s * r0[:, 1], s * r0[:, 0] + c * r0[:, 1]], axis=-1)
    return r, Om, dt


def prueba_1a(N=300, sigma=1.0, seed=0, n_grid=41,
              Ts=(51, 102, 204, 408), hs=(0.2, 0.35, 0.5)):
    """Identidad exacta usada como referencia (gaussiano, cualquier conjunto de muestras):
        sum_k K(r - b_k) b_k / sum_k K(r - b_k) = r + h^2 grad ln P_B(r)
    Velocidad exacta del esquema:
        medio:    v_k = Om_eff Jm b_k,  Om_eff = 2 tan(Om dt/2)/dt
        adelante: v_k = (sin(Om dt) Jm - (1 - cos(Om dt)) I) r_k / dt
    => omega_ref = Om_eff (2 + h^2 lap ln P_B), con P_B = densidad de los anclajes b_k.
    Para N -> infinito y nube gaussiana, el valor medio esperado es 2 Om sigma^2/(sigma^2 + h^2)."""
    print("\n=== 1a. Rotación rígida ===")
    X, Y, G = malla((-2.5 * sigma,) * 2, (2.5 * sigma,) * 2, n_grid)
    i0 = np.argmin((G ** 2).sum(1))                     # punto de malla más cercano al origen
    filas = []
    for T in Ts:
        r, Om, dt = rotacion_rigida(N, T, sigma, seed)
        th = Om * dt
        for h in hs:
            for esq in ("adelante", "medio"):
                A, B, Vel = muestras(r, dt, esq, cerrado=True)
                P, gP, lP = densidad_kde(G, A, h)
                J, gJ = corriente_kde(G, B, Vel, h)
                F = campos_derivados(P, gP, lP, J, gJ)       # operativo: P de r_k
                mask = P > MASK_FRAC * P.max()
                # comprobación algebraica del código: u calculado con la densidad de los anclajes
                PB, gPB, lPB = densidad_kde(G, B, h)
                FB = campos_derivados(PB, gPB, lPB, J, gJ)
                Om_eff = 2 * np.tan(th / 2) / dt if esq == "medio" else np.sin(th) / dt
                om_ref = Om_eff * (2 + h ** 2 * FB["lap_lnP"])
                err_id = np.max(np.abs(FB["omega"][mask] - om_ref[mask])) / (2 * Om)
                filas.append(dict(
                    T=T, h=h, esquema=esq,
                    err_identidad=err_id,
                    div_rel=div_relativa(F, mask, h),
                    omega_med_2Om=np.mean(F["omega"][mask]) / (2 * Om),
                    omega_origen_2Om=F["omega"][i0] / (2 * Om),
                    ref_origen_2Om=om_ref[i0] / (2 * Om),
                    gauss_inf=sigma ** 2 / (sigma ** 2 + h ** 2),
                ))
    df = pd.DataFrame(filas)
    _guardar(df, "b1a_rotacion.csv")
    return df


# ============================================================
# 1b. Ornstein-Uhlenbeck 2D con rotación
# ============================================================
def simular_ou(gamma, Om, D, dt, nsteps, seed):
    """dr = -(gamma I + Om Jm) r dt + sqrt(2D) dW, muestreo EXACTO (sin error de Euler):
        r_{k+1} = e^{-gamma dt} R(-Om dt) r_k + xi,   xi ~ N(0, s (1 - e^{-2 gamma dt}) I),
    con s = D/gamma la varianza estacionaria por eje. Arranca en el estado estacionario."""
    rng = np.random.default_rng(seed)
    s = D / gamma
    a = np.exp(-gamma * dt)
    th = -Om * dt
    c, sn = a * np.cos(th), a * np.sin(th)
    xi = rng.normal(0.0, np.sqrt(s * (1 - a * a)), (nsteps, 2)).tolist()
    x, y = rng.normal(0.0, np.sqrt(s), 2).tolist()
    r = np.empty((nsteps, 2))
    for k in range(nsteps):
        r[k, 0] = x
        r[k, 1] = y
        x, y = c * x - sn * y + xi[k][0], sn * x + c * y + xi[k][1]
    return r


def prueba_1b(gamma=1.0, Om=1.0, D=1.0, t_total=5000.0, n_grid=25,
              dts=(0.05, 0.01), hs=(0.35,), seeds=(0, 1, 2)):
    """Soluciones analíticas (s = D/gamma):
        P_ss = N(0, s I),  F = -(gamma I + Om Jm) r,
        v = F - D grad ln P_ss = -Om Jm r   (velocidad de corriente),  rot v = -2 Om.
    Suavizadas con el kernel (c_h = s/(s + h^2)):
        U_h = |r|^2 / (2 (s + h^2)) + cte
        medio    -> u_h = -c_h Om Jm r                : radial 0,      azimutal -Om
        adelante -> u_h = -c_h (gamma I + Om Jm) r    : radial -gamma, azimutal -Om   (dt -> 0)
        en ambos  omega_h = -2 Om c_h
    Las columnas 'radial' y 'azimutal' están divididas por c_h |r|."""
    print("\n=== 1b. Ornstein-Uhlenbeck 2D ===")
    s = D / gamma
    L = 2.5 * np.sqrt(s)
    X, Y, G = malla((-L, -L), (L, L), n_grid)
    rr = np.sqrt((G ** 2).sum(1))
    ok_r = rr > 0.2 * np.sqrt(s)
    rhat = np.zeros_like(G)
    phat = np.zeros_like(G)
    rhat[ok_r] = G[ok_r] / rr[ok_r, None]
    phat[ok_r] = np.column_stack([-G[ok_r, 1], G[ok_r, 0]]) / rr[ok_r, None]
    filas = []
    for dt in dts:
        nsteps = int(round(t_total / dt))
        for seed in seeds:
            t0 = time.time()
            r = simular_ou(gamma, Om, D, dt, nsteps, seed)
            for h in hs:
                c_h = s / (s + h ** 2)
                A, _, _ = muestras(r, dt, "adelante", cerrado=False)
                P, gP, lP = densidad_kde(G, A, h)
                mask = P > MASK_FRAC * P.max()
                mr = mask & ok_r
                U_pred = rr ** 2 / (2 * (s + h ** 2))
                for esq in ("adelante", "medio"):
                    _, B, Vel = muestras(r, dt, esq, cerrado=False)
                    J, gJ = corriente_kde(G, B, Vel, h)
                    F = campos_derivados(P, gP, lP, J, gJ)
                    dU = F["U"][mask] - U_pred[mask]
                    u = F["u"]
                    filas.append(dict(
                        dt=dt, seed=seed, h=h, esquema=esq,
                        radial=np.median((u * rhat).sum(1)[mr] / (c_h * rr[mr])),
                        azimutal=np.median((u * phat).sum(1)[mr] / (c_h * rr[mr])),
                        omega_rel=np.median(F["omega"][mask]) / (-2 * Om * c_h),
                        u2_rel=np.median((u ** 2).sum(1)[mr] / ((Om * c_h * rr[mr]) ** 2)),
                        div_rel=div_relativa(F, mask, h),
                        U_rmse_rel=np.sqrt(np.mean((dU - dU.mean()) ** 2)) / np.ptp(U_pred[mask]),
                    ))
            print(f"  dt={dt} seed={seed}: {time.time() - t0:.1f} s")
    df = pd.DataFrame(filas)
    _guardar(df, "b1b_ou.csv")
    print("\nPromedio ± desv. estándar entre semillas:")
    agg = df.drop(columns="seed").groupby(["dt", "h", "esquema"]).agg(["mean", "std"])
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(agg.to_string(float_format=lambda v: f"{v:.3g}"))
    return df


# ============================================================
# 1c. Fock-Darwin con la ecuación maestra (malla y ruido)
# ============================================================
def _lap5(F, dx):
    out = np.full_like(F, np.nan)
    out[1:-1, 1:-1] = (F[2:, 1:-1] + F[:-2, 1:-1] + F[1:-1, 2:] + F[1:-1, :-2]
                       - 4 * F[1:-1, 1:-1]) / dx ** 2
    return out


def fock_darwin(n_grid, L=4.0, w0=1.0, wc=2.0, l=1, ruido=0.0, seed=0):
    """Estado n=0 de Fock-Darwin, unidades hbar = m = q = 1, gauge simétrico
    A = (B0/2)(-y, x), B0 = m wc / q, S = hbar l phi.
        P ∝ r^{2|l|} exp(-m Om r^2 / hbar),   Om^2 = w0^2 + wc^2/4
        E = (|l| + 1) hbar Om - l hbar wc / 2   (n = 0)
    Con este E, la ecuación maestra da exactamente V = (1/2) m w0^2 r^2.
    Las derivadas se calculan con diferencias finitas en la malla (P y S son datos en la malla).
    Ruido: P -> P (1 + ruido * xi), xi ~ N(0, 1) i.i.d. por punto."""
    hbar = m = q = 1.0
    B0 = m * wc / q
    Om = np.sqrt(w0 ** 2 + wc ** 2 / 4)
    x = np.linspace(-L, L, n_grid)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x, indexing="ij")
    r2 = X ** 2 + Y ** 2
    P_ex = r2 ** abs(l) * np.exp(-m * Om * r2 / hbar)
    P = P_ex.copy()
    if ruido > 0:
        P = P * (1 + ruido * np.random.default_rng(seed).standard_normal(P.shape))
    P = np.clip(P, 1e-300, None)
    # grad S a partir de z = exp(iS/hbar), sin corte de rama: grad S = hbar Im(conj(z) grad z)
    z = np.exp(1j * l * np.arctan2(Y, X))
    zx, zy = np.gradient(z, dx, dx)
    Sx = hbar * np.imag(np.conj(z) * zx)
    Sy = hbar * np.imag(np.conj(z) * zy)
    px, py = Sx - q * (-B0 * Y / 2), Sy - q * (B0 * X / 2)       # grad S - q A
    flujo = -(px ** 2 + py ** 2) / (2 * m)
    E = (abs(l) + 1) * hbar * Om - l * hbar * wc / 2
    gPx, gPy = np.gradient(P, dx, dx)
    with np.errstate(divide="ignore", invalid="ignore"):
        bohm_P = hbar ** 2 / (4 * m) * (_lap5(P, dx) / P - 0.5 * (gPx ** 2 + gPy ** 2) / P ** 2)
        R = np.sqrt(P)
        bohm_R = hbar ** 2 / (2 * m) * _lap5(R, dx) / R
    V_ex = 0.5 * m * w0 ** 2 * r2
    interior = np.zeros_like(P, bool)
    interior[2:-2, 2:-2] = True
    m5 = interior & (P_ex > MASK_FRAC * P_ex.max())
    m_amplia = interior & (P_ex > 1e-6 * P_ex.max()) & (r2 > (3 * dx) ** 2)
    m_origen = interior & (r2 < 0.3 ** 2) & (r2 > 0)
    res = []
    for forma, bohm in (("P", bohm_P), ("sqrtP", bohm_R)):
        err = E + flujo + bohm - V_ex
        e5 = err[m5]
        res.append(dict(
            n_grid=n_grid, dx=dx, ruido=ruido, forma=forma,
            rmse_m5=np.sqrt(np.mean(e5 ** 2)),
            rmse_m5_forma=np.sqrt(np.mean((e5 - e5.mean()) ** 2)),
            sesgo_m5=e5.mean(),
            rmse_amplia=np.sqrt(np.mean(err[m_amplia] ** 2)),
            maxerr_r_lt_0p3=np.max(np.abs(err[m_origen])) if m_origen.any() else np.nan,
            rango_Vex_m5=np.ptp(V_ex[m5]),
            pred_ruido=0.25 * np.sqrt(20) * ruido / dx ** 2,
        ))
    return res


def prueba_1c(grids=(65, 129, 257), ruidos=(0.0, 1e-4, 1e-3, 1e-2)):
    """pred_ruido = (1/4) sqrt(20) eps / dx^2: desviación estándar esperada del término de Bohm
    por ruido blanco multiplicativo (orden dominante, estencil de 5 puntos)."""
    print("\n=== 1c. Fock-Darwin (n=0, l=1, w0=1, wc=2) ===")
    filas = []
    for n in grids:
        for e in ruidos:
            filas += fock_darwin(n, ruido=e)
    df = pd.DataFrame(filas)
    _guardar(df, "b1c_fock_darwin.csv")
    sin = df[df.ruido == 0].sort_values(["forma", "n_grid"])
    print("\nOrden de convergencia sin ruido (log2 del cociente de RMSE al dividir dx por 2):")
    for forma, g in sin.groupby("forma"):
        v = g["rmse_m5"].to_numpy()
        print(f"  {forma:6s}: " + ", ".join(f"{np.log2(v[i] / v[i + 1]):.2f}" for i in range(len(v) - 1)))
    return df


if __name__ == "__main__":
    pruebas = {"1a": prueba_1a, "1b": prueba_1b, "1c": prueba_1c}
    sel = sys.argv[1:] or list(pruebas)
    for k in sel:
        t0 = time.time()
        pruebas[k]()
        print(f"[{k}] {time.time() - t0:.1f} s")
