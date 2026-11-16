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
ESCENARIOS = {"rota": (8, 18), "debil": (8, 10), "no_rota": (8, 8)}


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
    flat = r.reshape(-1, 2)
    return (r - flat.mean(0)) / flat.std(0)


def area_con_signo(curva):
    """curva (H, 2); área del polígono cerrado (regla del zapato)."""
    c1 = np.roll(curva, -1, axis=0)
    return 0.5 * (curva[:, 0] * c1[:, 1] - c1[:, 0] * curva[:, 1]).sum()


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
    for nombre, (c_out, c_in) in ESCENARIOS.items():
        t0 = time.time()
        r = simular(c_out, c_in, rng)
        r_std = estandarizar(r)
        curva_media = r_std.mean(1)                          # (H, 2)
        A_media = area_con_signo(curva_media)
        A_dias = np.array([area_con_signo(r_std[:, d]) for d in range(ND)])

        S = r_std.reshape(-1, 2)
        _, _, G = malla(S.min(0) - 1.0, S.max(0) + 1.0, N_GRID)
        F = campos(r_std, G, H_KDE)
        mask = F["P"] > MASK_FRAC * F["P"].max()
        Pm = F["P"][mask]
        D_hat = 0.5 * np.var(A_dias)                         # escala de difusión del área (proxy)
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
            A_nulo[i] = area_con_signo(rr.mean(1))
        p = 2 * min((A_nulo >= A_media).mean(), (A_nulo <= A_media).mean())

        filas.append(dict(escenario=nombre, c_out=c_out, c_in=c_in, A_media=A_media,
                          A_dias_media=A_dias.mean(), A_dias_sd=A_dias.std(),
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
    ver("C4 el flujo aporta en 'rota' (flujo/Bohm > 0.1)", g.loc["rota", "flujo_sobre_bohm"] > 0.1,
        f"{g.loc['rota', 'flujo_sobre_bohm']:.3g}")
    ver("C5 'debil' queda entre medias en |A| y vorticidad", 
        abs(g.loc["no_rota", "A_media"]) < abs(g.loc["debil", "A_media"]) < abs(g.loc["rota", "A_media"]),
        f"|A|: no_rota {abs(g.loc['no_rota', 'A_media']):.3f}, debil {abs(g.loc['debil', 'A_media']):.3f}, rota {abs(g.loc['rota', 'A_media']):.3f}")


if __name__ == "__main__":
    main()
