# Bloque 9b: chequeo de consistencia con intervalo propio, calibración y ruido mayor

```bash
cd NucleoTG/analisis
python b9b_chequeo.py     # estimado: 12-20 min
```

Salidas: tabla resumen, lista de criterios con CUMPLE o NO CUMPLE, `resultados/b9b_resultados.csv` y `b9b_hboot.csv`.

## Por qué existe
En el bloque 9 falló B0. El chequeo de consistencia con umbral fijo (\|disc\| > 0.25) dio una falsa alarma en 1 de 3 semillas de la línea base. La causa es que la tasa de la autocorrelación tiene una dispersión de ±16 % entre semillas, frente a ±2 % del hamiltoniano. Con datos reales solo hay un conjunto de datos, así que el chequeo necesita su propia incertidumbre.

## Cambios de método (decididos antes de ejecutar)
1. **Bandera = a0 fuera del intervalo del 95 % de la tasa de la autocorrelación.** El intervalo sale de remuestrear trayectorias (B = 500), con la ventana de ajuste fija a partir de los datos completos. Si la ventana dura menos de 1 unidad de tiempo, la bandera se activa.
2. **La ventana empieza en τ = 3.** El modo real más lento de H está en ≈ 1.4 (bloque 8, columna `nota`). Con τ = 1 todavía aporta e^{−1.4} ≈ 0.25 de amplitud relativa; con τ = 3, ≈ 0.015. Se reporta también τ = 1 (`flag_t1`) para comparar.
3. **Solo se usa la incertidumbre de la autocorrelación.** Se apoya en el bloque 9 (H ±2 % frente a ±16 %) y se comprueba en la prueba 5.
4. **Corrección por ruido de medición.** Si el ruido se suma al suavizado, h_ef² = h² + σ², de modo que a0_corr = a0 − c_fit·σ̂², con c_fit la pendiente del propio ajuste en h² y σ̂ la ordenada del estimador robusto de D. Predicción, con c = 13.57 del bloque 8b: sesgo ≈ 13.57·σ²/0.1065, es decir +5.1 % (σ = 0.02), +31.9 % (σ = 0.05) y +127 % (σ = 0.1). Para σ = 0.01 da +1.3 %, y el bloque 9 midió +1.1 %, una sola comprobación a favor.

## Criterios declarados ANTES de ejecutar
| id | condición | si falla |
|---|---|---|
| **C1** falsos positivos | bandera en ≤ 10 % de 20 semillas de la línea base (≤ 2 de 20) | el chequeo no es fiable aun con intervalo; no se puede usar para descartar datos reales |
| **C2** potencia, deriva ε = 0.05 | bandera en ≥ 80 % de 10 semillas | el chequeo no detecta no estacionariedad moderada |
| **C3** potencia, proyección κ = 1.5 | bandera en ≥ 80 % de 10 semillas | el chequeo no detecta memoria por proyección |
| **C4** ley del ruido | sesgo sin corregir a ±30 % (relativo) del predicho, para σ = 0.02 y 0.05 (5 semillas) | el ruido no actúa como suavizado extra; la corrección no tiene base |
| **C5** corrección | \|err_ref_corr\| ≤ 0.10 para σ = 0.02 y 0.05 | la corrección no basta |
| **C6** supuesto de la bandera | desviación de H por remuestreo ≤ 0.5 de la de la autocorrelación, en las 3 semillas | hay que incluir la incertidumbre de H en el chequeo |

Sin criterio, solo se reportan: deriva ε = 0.02, proyección κ = 1.0, σ = 0.1, la versión con τ = 1 y la versión del ruido con D_std.

## Expectativas (no son pruebas)
- **C1:** incierto. Si hay un sesgo sistemático entre las dos vías (el bloque 9 dio disc medio de +0.10 con τ = 1), un intervalo honesto dará más falsos positivos que el 5 % nominal. Por eso el umbral es 10 %. τ = 3 debería reducir ese sesgo, si venía de los modos rápidos.
- **C2:** probable, porque en el bloque 9 la discrepancia era ≈ −0.6.
- **C3:** incierto (bloque 9: \|disc\| = 0.32 con κ = 1.5, solo 3 semillas).
- **C4 y C5:** la ley tiene una sola comprobación a favor (σ = 0.01). Con σ = 0.1, h_ef ≈ 0.11 cae fuera del intervalo del ajuste (h ≤ 0.08), y no espero que la corrección funcione.

## Límites
- La prueba 5 usa un solo h (0.04) y 10 remuestreos. La dispersión de a0 extrapolado (4 valores de h) podría ser mayor. Con B_H = 10, la desviación estimada tiene una incertidumbre de ~25 %.
- Las semillas de potencia comparten numeración entre condiciones, pero los generadores se desplazan por condición; no son las mismas trayectorias.
- Todo en el mismo sistema (Stuart–Landau con μ = 1, ω = 2π, β = 1). La ley del ruido y la tasa de falsos positivos podrían cambiar con otra geometría o con otra frecuencia de muestreo.
