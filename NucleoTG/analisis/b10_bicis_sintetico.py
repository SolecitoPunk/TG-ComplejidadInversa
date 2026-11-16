"""
Bloque 10: sintético de bicicletas compartidas, prueba de viabilidad antes de usar datos reales.

    python b10_bicis_sintetico.py          # ~4-8 min

Modelo del "día" de una ciudad. Estado 2D s(t) = (salidas, llegadas) por hora, a lo largo de 24 h.
El día se repite ND veces con ruido de día a día. Interpretación: un día es un "ciclo"; el conjunto
de días es el ensemble a partir del cual se estiman densidad, corriente y difusión.

Dinámica subyacente (declarada): proceso en el plano de intensidades latentes a_out(t), a_in(t), cada
una un ciclo límite ruidoso centrado en su hora pico. Las observaciones por hora son recuentos; el
ruido de observación se añade aparte.

Escenarios (criterio: el método debe distinguirlos):
  "rota"    picos desfasados (salidas 8 h, llegadas 18 h): el estado gira -> vorticidad != 0, el flujo aporta
  "no_rota" picos a la misma hora: el estado sube y baja por la misma recta -> vorticidad ~ 0, el flujo no aporta
  "debil"   desfase pequeño (2 h): caso intermedio

Para cada escenario se calculan, sobre el ensemble de días:
  - area con signo del lazo medio (sin kernel): detector directo de rotación
  - P, u, vorticidad y circulacion Gamma (con kernel)
  - D estimada de la dispersion dia-a-dia; termino de flujo frente al de Bohm con lambda = 2D
  - modelo nulo por hora (desfase circular del eje de llegadas): intervalo de la vorticidad nula
Criterios en README_bloque10.md (declarados antes de ejecutar).

Esto NO es aún la ecuación de Madelung-Bohm como modelo generativo falsable (eso requiere la parte
espectral del bloque 8). Aquí se prueba si el estado 2D de un sistema tipo bicis tiene un flujo
rotacional separable del ruido, que es la condición previa para que la ecuación aporte algo.
"""
import os
import time

import numpy as np

from campos import malla, muestras, densidad_kde, corriente_kde, campos_derivados

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
SEED = 3
H = 24                      # horas por día
ND = 300                    # días (ciclos)
SIGMA_DIA = 0.20            # ruido relativo de día a día
RUIDO_OBS = 0.05            # ruido de observación relativo
N_GRID = 40
H_KDE = 0.35
MASK_FRAC = 0.05
N_NULO = 400
# Desfase como fracción del ciclo de 24 h. El giro es MÁXIMO en cuadratura (1/4 de ciclo, seno/coseno)
# y NULO tanto en fase (0) como en oposición de fase (1/2): con perfiles simétricos la curva va y vuelve
# por la misma recta. Por eso:
#   rota     = 1/4  (6 h, cuadratura, giro máximo)
#   debil    = 1/16 (1.5 h, casi en fase)
#   no_rota  = 0    (en fase)
#   anti_fase= 1/2  (12 h, oposición de fase: tampoco gira; control de que el máximo no está ahí)
ESCENARIOS = {"rota": 0.25, "debil": 0.0625, "no_rota": 0.0, "anti_fase": 0.5}
C_BASE = 8.0


def perfil(t, centro, ancho=3.0):
    d = ((t - centro + 12) % 24) - 12
    return np.exp(-0.5 * (d / ancho) ** 2)


def simular(c_out, c_in, rng):
    """Devuelve r (H, ND, 2): para cada día, la curva horaria del estado (salidas, llegadas).
    Las intensidades latentes fluctúan día a día (SIGMA_DIA) y hora a hora comparten esa fluctuación
    de forma suave (un factor por día), más ruido de observación por hora (RUIDO_OBS)."""
    t = np.arange(H)
    base_out = perfil(t, c_out)
    base_in = perfil(t, c_in)
    fac_out = 1 + SIGMA_DIA * rng.standard_normal(ND)       # factor de escala del día
    fac_in = 1 + SIGMA_DIA * rng.standard_normal(ND)
    out = base_out[:, None] * fac_out[None, :] * (1 + RUIDO_OBS * rng.standard_normal((H, ND)))
    inn = base_in[:, None] * fac_in[None, :] * (1 + RUIDO_OBS * rng.standard_normal((H, ND)))
    return np.stack([out, inn], axis=-1)                    # (H, ND, 2)


def estandarizar(r):
    """Estandariza cada eje por separado (media 0, varianza 1). Mantener la escala por eje evita
    que un desfase pequeño, que correlaciona los ejes, infle el área: el lazo se mide sobre
    variables de varianza unitaria, no sobre una nube estirada en la diagonal."""
    flat = r.reshape(-1, 2)
    return (r - flat.mean(0)) / flat.std(0)


def area_con_signo(curva):
    """curva (H, 2); área del polígono cerrado (regla del zapato). Para comparar entre escenarios se
    reporta también normalizada por el radio medio de la curva (área de un círculo de ese radio = pi r^2),
    de modo que 'cuánto gira' no dependa de cuánto se estira el lazo."""
    c1 = np.roll(curva, -1, axis=0)
    A = 0.5 * (curva[:, 0] * c1[:, 1] - c1[:, 0] * curva[:, 1]).sum()
    centro = curva.mean(0)
    rad = np.linalg.norm(curva - centro, axis=1).mean()
    A_norm = A / (np.pi * rad ** 2) if rad > 0 else 0.0     # 1 = círculo perfecto; ~0 = ida y vuelta
    return A, A_norm


def estimar_D(r_std):
    """Difusión en el plano de estados a partir de los incrementos horarios de cada día (segundas
    diferencias, que cancelan la deriva a primer orden): D = <|r_{k+2} - 2 r_{k+1} + r_k|^2> / (8 dt),
    con dt = 1/H (el día normalizado a 1). Misma definición que los bloques 8-9."""
    dt = 1.0 / r_std.shape[0]
    dd = r_std[2:] - 2 * r_std[1:-1] + r_std[:-2]           # (H-2, ND, 2)
    return float((dd ** 2).sum(-1).mean() / (8 * dt))


def campos(r_std, G, h):
    """r_std (H, ND, 2): cada día es una trayectoria cerrada en el tiempo. Se trata el conjunto
    de días como el ensemble; la corriente usa la velocidad temporal (punto medio) de cada día."""
    Hn, ND_, _ = r_std.shape
    A, B, V = muestras(r_std, 1.0 / Hn, "medio", cerrado=True)
    P, gP, lP = densidad_kde(G, A, h)
    J, gJ = corriente_kde(G, B, V, h)
    return campos_derivados(P, gP, lP, J, gJ)


def main():
    rng = np.random.default_rng(SEED)
    os.makedirs(OUT, exist_ok=True)
    import pandas as pd
    filas = []
    for nombre, frac in ESCENARIOS.items():
        t0 = time.time()
        c_out = C_BASE - 12 * frac
        c_in = C_BASE + 12 * frac
        r = simular(c_out, c_in, rng)
        r_std = estandarizar(r)
        curva_media = r_std.mean(1)                          # (H, 2)
        A_media, A_norm = area_con_signo(curva_media)
        A_dias = np.array([area_con_signo(r_std[:, d])[0] for d in range(ND)])

        S = r_std.reshape(-1, 2)
        _, _, G = malla(S.min(0) - 1.0, S.max(0) + 1.0, N_GRID)
        F = campos(r_std, G, H_KDE)
        mask = F["P"] > MASK_FRAC * F["P"].max()
        Pm = F["P"][mask]
        D_hat = estimar_D(r_std)                             # difusión en el plano de estados (bloques 8-9)
        lam = 2 * D_hat
        vort_media = float((Pm * F["omega"][mask]).sum() / Pm.sum())
        rango_flujo = float(np.ptp(F["flujo"][mask]))
        rango_bohm = float(lam * np.ptp(F["bohm1"][mask]))

        # nulo: desfase circular del eje de llegadas por día (rompe la relación temporal entre ejes)
        A_nulo = np.empty(N_NULO)
        for i in range(N_NULO):
            rr = r_std.copy()
            for d in range(ND):
                rr[:, d, 1] = np.roll(rr[:, d, 1], rng.integers(H))
            A_nulo[i] = area_con_signo(rr.mean(1))[0]
        p = 2 * min((A_nulo >= A_media).mean(), (A_nulo <= A_media).mean())

        filas.append(dict(escenario=nombre, desfase_frac=frac, c_out=c_out, c_in=c_in,
                          A_media=A_media, A_norm=A_norm, A_dias_sd=A_dias.std(),
                          vort_media_P=vort_media, D_hat=D_hat,
                          rango_flujo=rango_flujo, rango_bohm_2D=rango_bohm,
                          flujo_sobre_bohm=rango_flujo / rango_bohm if rango_bohm > 0 else np.nan,
                          nulo_p2_5=np.percentile(A_nulo, 2.5), nulo_p97_5=np.percentile(A_nulo, 97.5),
                          p_rotacion=min(1.0, p)))
        print(f"  {nombre}: {time.time() - t0:.1f} s")

    df = pd.DataFrame(filas)
    df.to_csv(os.path.join(OUT, "b10_bicis.csv"), index=False)
    with pd.option_context("display.width", 240, "display.max_columns", 30):
        print("\n=== Sintético de bicicletas ===")
        print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))

    def ver(n, ok, d):
        print(f"  [{'CUMPLE' if ok else 'NO CUMPLE'}] {n}: {d}")
    print("\n=== Criterios declarados ===")
    g = df.set_index("escenario")
    ver("C1 'rota' tiene rotación significativa (p < 0.05)", g.loc["rota", "p_rotacion"] < 0.05,
        f"p = {g.loc['rota', 'p_rotacion']:.3g}, A_media = {g.loc['rota', 'A_media']:.3f}")
    ver("C2 'no_rota' NO es significativo (p >= 0.05)", g.loc["no_rota", "p_rotacion"] >= 0.05,
        f"p = {g.loc['no_rota', 'p_rotacion']:.3g}, A_media = {g.loc['no_rota', 'A_media']:.3f}")
    ver("C3 |vort(rota)| > 3 |vort(no_rota)|", abs(g.loc["rota", "vort_media_P"]) > 3 * abs(g.loc["no_rota", "vort_media_P"]),
        f"{g.loc['rota', 'vort_media_P']:.3f} frente a {g.loc['no_rota', 'vort_media_P']:.3f}")
    fb = g.loc["rota", "flujo_sobre_bohm"]
    ver("C4 el flujo aporta en 'rota' y en rango sensato (0.1 <= flujo/Bohm <= 10)", 0.1 <= fb <= 10,
        f"flujo/Bohm = {fb:.3g}, D_hat = {g.loc['rota', 'D_hat']:.3g}")
    ver("C5 'rota' (cuadratura) es el que más gira: |A_norm| mayor que 'debil', 'no_rota' y 'anti_fase'",
        abs(g.loc["rota", "A_norm"]) > max(abs(g.loc[e, "A_norm"]) for e in ("debil", "no_rota", "anti_fase")),
        "|A_norm|: " + ", ".join(f"{e} {abs(g.loc[e, 'A_norm']):.3f}" for e in ESCENARIOS))
    ver("C6 'anti_fase' (oposición) NO es significativo (p >= 0.05): el máximo no está en medio ciclo",
        g.loc["anti_fase", "p_rotacion"] >= 0.05,
        f"p = {g.loc['anti_fase', 'p_rotacion']:.3g}, A_norm = {g.loc['anti_fase', 'A_norm']:.3f}")


if __name__ == "__main__":
    main()
