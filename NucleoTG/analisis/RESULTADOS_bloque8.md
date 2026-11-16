# Resultados del bloque 8 (ejecutado por el autor; una semilla)

Referencias: FP verdadero en la misma malla. OU: 1 ± 3i. Stuart–Landau: 0.1065 ± 5.267i.

## A. OU, control del código: no se cumple por poco
| fuente | tasa | frecuencia | |λ₀| | solape con √P̂ |
|---|---|---|---|---|
| FP verdadero | 1.000 | 3.000 | 4e-5 | |
| autocorrelación | 0.973 | 2.968 | | |
| H reconstruido, h = 0.15, máscara 1e-4 | 0.969 | **2.841** | 0.0014 | 0.9999 |
| H reconstruido, h = 0.15, máscara 1e-6 | 0.958 | **2.843** | 9e-5 | 1 |
| H reconstruido, h = 0.30 | 0.857 | 2.517 | 0.0011 | 0.9999 |

Criterio: \|b − 3\| ≤ 0.15; se obtuvo 0.159 y 0.157. **No se cumple.** El umbral no se relaja. Los demás criterios de A se cumplen. El sesgo crece con h, como en el suavizado del bloque 1b. Que sea sesgo de estimación y no error de ensamblado se comprueba en el bloque 8b (control con campos exactos).

## B. Stuart–Landau: se cumple
| fuente | difusión de fase | frecuencia |
|---|---|---|
| FP verdadero | 0.1065 | 5.267 |
| autocorrelación | 0.1162 (+9.1 %) | 5.272 |
| H reconstruido, h = 0.04, máscara 1e-4 | **0.1296 (+21.7 %)** | 5.262 (−0.1 %) |
| H reconstruido, h = 0.04, máscara 1e-6 | 0.1292 (+21.3 %) | 5.261 |
| H reconstruido, h = 0.08 | 0.1964 (+84 %) | 5.236 |

Criterio: frecuencia dentro del 5 % y tasa dentro del 30 % con al menos un h. Se cumple con h = 0.04. La frecuencia es robusta en todos los casos; la tasa de relajación depende de h.

## C. Datos limitados (10 %, unos 840 ciclos): se cumple por un pelo
h = 0.04: 0.1381 (+29.7 %) y frecuencia 5.272; con máscara 1e-6, 0.1375 (+29.1 %). La autocorrelación da 0.0928 (−12.9 %). Margen de 0.3 puntos porcentuales.

## Observaciones
- D̂ coincide con D: 0.5003 y 0.05002.
- Exceso de la tasa sobre el valor verdadero: 0.0231 con h = 0.04 y 0.0899 con h = 0.08. Razón 3.9, cercana a 4, el valor de una ley en h². Son dos puntos y no confirman la ley; el bloque 8b usa cuatro valores de h.
- Una semilla y un solo valor de D: sin barra de error.
- Los supuestos del método se cumplen por construcción (D constante e isotrópica, Markov en 2D, estacionariedad, muchos ciclos).
