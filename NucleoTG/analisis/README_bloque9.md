# Bloque 9: el benchmark Stuart–Landau con violaciones realistas

```bash
cd NucleoTG/analisis
python b9_violaciones.py     # estimado: 6-10 min (3 semillas, 13 condiciones)
```

Salida: tabla resumen por violación y nivel, lista de criterios con CUMPLE o NO CUMPLE, y `resultados/b9_resultados.csv` con todas las filas.

## Qué se prueba
La prueba de viabilidad (b8, b8b) se cumplió con todos los supuestos satisfechos por construcción. Aquí se rompe un supuesto cada vez, con tres niveles, sobre el mismo Stuart–Landau (μ = 1, ω = 2π, β = 1, D = 0.05; 20 trayectorias de 200 unidades de tiempo, unos 3400 ciclos).

| violación | cómo se introduce | verdad de referencia |
|---|---|---|
| V1 ruido de medición | ruido blanco σ = 0.002, 0.005, 0.01 sumado a las mismas trayectorias de la línea base. El radio del ciclo es 1 y su ancho ≈ 0.16 | espectro del sistema sin ruido (re = 0.1065) |
| V2 difusión anisotrópica | Dx/Dy = q = 1.5, 2, 4 con (Dx + Dy)/2 = D | operador de Fokker–Planck con D diagonal, calculado en la malla |
| V3 proyección | se observa solo z₁ de un sistema 4D: z₁ acoplado a un oscilador amortiguado z₂ (γ₂ = 2, ω₂ = 3, coef. de acoplamiento κ = 0.5, 1, 1.5) | **no hay**: la verdad del sistema observado no es un proceso de Markov en 2D |
| V4 deriva lenta | μ(t) y ω(t) varían con amplitud relativa ε = 0.02, 0.05, 0.10 y periodo 50 (frente a 1.19 del ciclo), con fase al azar por trayectoria | sistema sin deriva (re = 0.1065); es la referencia del sistema congelado |

Para cada condición se calcula la tasa de relajación del primer modo oscilatorio de H con h = 0.03, 0.04, 0.06, 0.08, extrapolada a h → 0 con re = a₀ + c·h² (b8b), y la autocorrelación de z/|z| como medida independiente.

Estadísticos:
- **err_ref** = a₀/verdad − 1 (si hay verdad).
- **disc** = a₀/re_autocorrelación − 1. Es el chequeo de consistencia: solo usa los datos, y es lo que se tendría con datos reales.
- **resid_h2**: residuo del ajuste en h². Segundo detector posible, sin criterio.
- Umbral de bandera: |disc| > 0.25 (declarado ahora, no ajustado).

D se estima de dos maneras. La estándar (b8) usa segundas diferencias. La robusta ajusta var(m) = 8·D·(m·dt) + 12σ², con m = 1 a 4: la pendiente da D y la ordenada da σ².

## Comprobado antes de ejecutar (Python puro, una trayectoria de 300 000 pasos)
| σ_obs | D_std (exceso frente a D) | exceso predicho 1.5σ²/(D·dt) | D_rob (exceso) | σ̂ |
|---|---|---|---|---|
| 0 | −0.1 % | 0 | +3.4 % | 0 |
| 0.002 | +2.3 % | +2.4 % | +3.4 % | 0 |
| 0.005 | +14.9 % | +15.0 % | +3.4 % | 0.0041 |
| 0.01 | +60.0 % | +60.0 % | +3.4 % | 0.0096 |

- La fórmula del inflado por ruido de medición es correcta.
- El estimador robusto no depende del ruido, con un sesgo fijo de +3.4 % por la curvatura de la trayectoria. Con σ pequeño, σ̂ no se resuelve (sale 0 con σ = 0.002).
- Con difusión anisotrópica q = 4 (Dx = 0.08, Dy = 0.02) los estimadores por eje dan 0.0799 y 0.0200. **El ruido de medición también inflaría Dx̂ y Dŷ:** con σ = 0.01 la razón estimada sería 2.2 en vez de 4. Por eso V2 se prueba sin ruido, y la razón no es fiable si hay ruido sin corregir.

## Criterios declarados ANTES de ejecutar
| id | condición | si falla |
|---|---|---|
| **B0** línea base | con las 3 semillas: \|err_ref\| ≤ 0.10, \|disc\| ≤ 0.25 (sin falsos positivos) y \|err_im\| ≤ 0.05 | los simuladores o estimadores nuevos son sospechosos; no se interpreta el resto |
| **V1a** | el exceso de D_std está a ±0.05 del predicho 1.5σ²/(D·dt) | la fórmula del ruido no describe esta simulación |
| **V1b** | \|D_rob/D − 1\| ≤ 0.10 en los tres niveles | el estimador robusto no sirve |
| **V1c** | con D_rob, \|err_ref\| ≤ 0.30 para σ ≤ 0.005 | el ruido de medición degrada P̂ o v̂ además de D̂; hace falta otro preprocesamiento |
| **V2a** | la razón Dx̂/Dŷ está a ±10 % de q | la anisotropía no es detectable |
| **V3** | \|disc\| > 0.25 con κ = 1.5 | el chequeo no detecta que el sistema no es markoviano en 2D; hay que declararlo como limitación |
| **V4** | \|disc\| > 0.25 con ε = 0.10 | el chequeo no detecta la no estacionariedad; ídem |

Sin criterio, solo se reportan:
- `err_ref` y `err_im` de V2 (mi expectativa: tolerable con q = 1.5 y peor al subir q; no la probé).
- `err_ref` de V4 frente al sistema congelado.
- `resid_h2` en todas las condiciones.

## Qué cambia según el resultado
- **V1b y V1c se cumplen:** el ruido de medición es manejable si se usa D_rob. La regla práctica para datos reales es calcular σ̂ y D_rob con el ajuste en m, y comparar con D_std. Si difieren mucho, el ruido domina y hay que corregir.
- **V1c falla:** con ruido de ese orden no se puede reconstruir H. Descartar datos neuronales sin un preprocesamiento (suavizado, promedio de ensayos, reducción de dimensión previa) que demuestre su efecto.
- **V3 o V4 fallan:** el chequeo de consistencia no es un detector fiable; en una propuesta debe presentarse como una condición necesaria, no como validación.
- **V2:** no cambia el veredicto de viabilidad, pero fija cuánta anisotropía tolera la formulación isotrópica. Una extensión con D anisótropa no está derivada.

## Límites
- Una violación a la vez; las combinaciones no se prueban (con datos reales ocurren todas juntas).
- El sistema 4D es un ejemplo con parámetros elegidos por mí. No cubre las proyecciones a 2D de datos neuronales en general (ver la crítica de Lebedev et al. 2019 sobre las rotaciones).
- 3 semillas por condición: las desviaciones estándar son orientativas.
- La deriva lenta de V4 tiene fase aleatoria por trayectoria. Con una deriva común a todas las trayectorias el resultado podría ser distinto.
- Las predicciones son expectativas, no pruebas. La única parte comprobada es la de los estimadores de D (tabla de arriba).
