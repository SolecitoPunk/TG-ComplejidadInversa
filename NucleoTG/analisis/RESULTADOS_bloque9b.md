# Resultados del bloque 9b (ejecutado por el autor; 906 s)

Referencia: re = 0.1065 (Stuart–Landau, D = 0.05). Bandera = a0 fuera del IC del 95 % de la tasa de la autocorrelación (remuestreo de trayectorias, B = 500; ventana τ ≥ 3).

## Criterios declarados
| id | resultado | estado |
|---|---|---|
| C1 falsos positivos ≤ 10 % | 1 de 20 (5 %); con τ_min = 1 también 1 de 20 | cumple |
| C2 potencia, deriva ε = 0.05 ≥ 80 % | 10 de 10 | cumple |
| C3 potencia, proyección κ = 1.5 ≥ 80 % | 10 de 10 | cumple |
| C4 sesgo por ruido = 13.57·σ²/ref a ±30 % (σ = 0.02 y 0.05) | observado 0.066 y 0.611; predicho 0.051 y 0.319 (cocientes 1.29 y 1.92) | **NO CUMPLE** |
| C5 corregido \|err\| ≤ 0.10 (σ = 0.02 y 0.05) | 0.018 y 0.423 | **NO CUMPLE** (solo σ = 0.02) |
| C6 dispersión de H ≤ 0.5 de la de la autocorrelación | razones 0.19, 0.32, 0.30 | cumple |

## Chequeo de consistencia
| condición | a0 | re_ac | se_ac | bandera |
|---|---|---|---|---|
| línea base (20 semillas) | 0.1066 (+0.1 %) | 0.1023 | 0.0098 | 1/20 |
| deriva ε = 0.02 | 0.1075 | 0.1485 | 0.0118 | 10/10 |
| deriva ε = 0.05 | 0.1080 | 0.3511 | 0.0291 | 10/10 |
| proyección κ = 1.0 | 0.0892 | 0.1168 | 0.0100 | 9/10 |
| proyección κ = 1.5 | 0.0557 | 0.0827 | 0.0081 | 10/10 |

- Con 20 semillas, 1 falsa alarma es compatible con 5 %, pero el intervalo de confianza de esa proporción es ≈ 0.1 %–25 %. Con 10 de 10, la cota inferior del 95 % para la potencia es ≈ 69 %.
- En deriva y proyección, a0 queda **por debajo** de la autocorrelación (descuadre negativo). En el ruido, **por encima**. Es una regularidad observada en un solo sistema con tres violaciones; no se probó que identifique el tipo de violación.
- La deriva de ε = 0.02 ya activa la bandera: el chequeo es muy sensible. En datos reales, casi cualquier heterogeneidad de frecuencia entre ciclos puede activarlo.

## Precisión de H frente a la autocorrelación
- Autocorrelación: error estándar de 0.0098 sobre 0.1023, es decir ≈ 10 %.
- H: dispersión de ≈ 2 % entre semillas (bloque 9) y ≈ 2.8 % por remuestreo con h = 0.04 (desviaciones 0.0027–0.0034, solo un h).
- **Corrección a una afirmación anterior** (bloque 8b: «la reconstrucción no es más precisa que la autocorrelación»): con ~3400 ciclos, H es 3–5 veces menos dispersa. La precisión no garantiza exactitud: con V3 es precisa y sesgada, y el chequeo es lo que lo detecta.

## Ruido de medición mayor (5 semillas, D robusto)
| σ | σ̂ | err_ref | err_ref corregido | bandera |
|---|---|---|---|---|
| 0.02 | 0.0198 | +6.6 % | +1.8 % | 1/5 |
| 0.05 | 0.0499 | +61 % | +42 % | 5/5 |
| 0.10 | 0.0999 | +409 % | +816 % | 5/5 |

- σ̂ recupera σ dentro del 1 % para σ ≥ 0.02.
- El sesgo supera la predicción de suavizado extra y crece más rápido que σ²: cocientes observado/predicho de 1.29, 1.92 y 3.2. El ruido de medición daña más que un suavizado equivalente, y el mecanismo no está identificado.
- Con σ = 0.1 el ajuste en h² tiene pendiente negativa, así que la corrección empeora el resultado (816 % frente a 409 %).
- Con D estándar: +101 %, +782 % y +3293 %. Con D robusto, el ruido de medición deja de ser un problema hasta σ ≈ 0.02 (13 % del ancho del ciclo, 2 % del radio).
- La bandera se activa en todos los casos con error grande. Con σ = 0.02 y D robusto solo en 1 de 5, con 1.8 % de error corregido.

## Punto de ruptura
Con D robusto y corrección, la reconstrucción funciona hasta σ ≈ 0.02 (σ/ancho del ciclo ≈ 0.13); con σ = 0.05 el error es del 42 % al 61 %. Esta regla sale de un solo sistema y tres niveles.

## Aviso sin resolver
La salida del bloque 4 (ruido) emitió «RuntimeWarning: invalid value encountered in add» en `H_reconstruido`. Mi hipótesis es que viene de celdas con P = 0, que quedan fuera de la máscara y no entran al operador. No lo he verificado; los resultados son finitos y coherentes.
