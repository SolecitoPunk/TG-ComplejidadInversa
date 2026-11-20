# Resultados del bloque 8b (ejecutado por el autor; 5 semillas)

Referencia (FP verdadero en la malla): Stuart–Landau re = 0.1065, im = 5.2666. OU: 1 ± 3i.

## 1. Control con campos exactos: se cumple
| sistema | re (exacto) | im (exacto) | err_re | err_im |
|---|---|---|---|---|
| OU | 1.011 | 2.998 | +1.1 % | −0.07 % |
| Stuart–Landau | 0.1070 | 5.266 | +0.5 % | −0.01 % |

Criterio: ambos errores ≤ 2 %. El ensamblado de H es correcto. El fallo del control A del bloque 8 (frecuencia de OU 2.841 con h = 0.15) es compatible con sesgo de estimación por el suavizado; no se probó variando h en OU.

## 2. Ley en h²: se cumple
Medias de 5 semillas, todos los datos (8382 ciclos):

| h | 0.03 | 0.04 | 0.06 | 0.08 |
|---|---|---|---|---|
| re | 0.1209 | 0.1288 | 0.1545 | 0.1953 |

Ajuste re = a0 + c·h²: **a0 = 0.1074 (+0.9 % frente a la referencia), c = 13.57, residuo relativo 0.8 %.** Criterio: residuo ≤ 5 % y a0 dentro del 10 %. El sesgo de la tasa de relajación sigue una recta en h² en el intervalo 0.03–0.08. Sin embargo: cuatro puntos y dos parámetros dejan solo 2 grados de libertad; el resultado es para este sistema y este intervalo de h.

## 3. Robustez en semillas: se cumple
h = 0.04, todos los datos: frac_ok = 5/5. re_sd = 0.0016, es decir 1.3 % de la media. El +21 % es un sesgo sistemático, no ruido de la semilla.

## 4. Datos necesarios (solo se reporta): fracción de semillas dentro de ±30 % en re y ±5 % en im
| ciclos | h = 0.03 | h = 0.04 | h = 0.06 | h = 0.08 |
|---|---|---|---|---|
| 8382 | 1.0 | 1.0 | 0 | 0 |
| 838 | 1.0 | 0.8 | 0 | 0 |
| 252 | 1.0 | 1.0 | 0 | 0 |
| 84 | 0.4 | 0.6 | 0 | 0 |

Con h ≥ 0.06 ninguna semilla cumple con ningún tamaño de datos: el sesgo (45 % y 83 %) agota la tolerancia. Con 84 ciclos la dispersión (re_sd = 0.017, 13–15 %) y el sesgo por ruido (+40 % con h = 0.03; hipótesis coherente con el bloque 1c, no comprobada) hacen que fallen la mitad de las semillas. Con 252 ciclos o más pasa con h = 0.03–0.04.

## Limitaciones de la lectura
- Las fracciones de datos son subconjuntos anidados de la misma simulación (los primeros pasos de cada trayectoria), así que no son independientes entre sí. La desviación estándar con 5 semillas tiene ella misma una incertidumbre de ~35 %: el valor re_sd = 0.0048 con 252 ciclos frente a 0.0074 con 838 no indica nada.
- Frecuencia: el error es < 1 % en todos los casos, así que no discrimina.
- El ancho del ciclo por linealización es σ = √(D/2) ≈ 0.16, de modo que h = 0.04 es 0.25σ y h = 0.08 es 0.5σ. Que el sesgo escale con (h/σ)² es una hipótesis; no se probó con otro D ni otra geometría.
- **La reconstrucción no es más precisa que la autocorrelación.** En el bloque 8, con todos los datos, la autocorrelación daba +9 % en la tasa y el hamiltoniano con h = 0.04 daba +21 %. Esta prueba valida la consistencia entre las dos vías (el espectro predice lo que se mide aparte). No muestra una ventaja en exactitud.
- Todo se hizo con los supuestos cumplidos por construcción: D constante e isotrópica, ruido sin medición, 2D sin memoria, estacionario.
