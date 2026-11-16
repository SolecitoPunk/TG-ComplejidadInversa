# Resultados del bloque 9 (ejecutado por el autor; 3 semillas, unos 3400 ciclos)

Referencias: re = 0.1065 e im = 5.2666 (isotrópica y anisotrópicas, q = 1.5, 2 y 4: 0.1065, 0.1065 y 0.1066).

## Criterios declarados

| id | resultado | estado |
|---|---|---|
| **B0** línea base | err_ref por semilla +1.4 %, −2.0 %, −0.7 % (cumple); err_im < 0.1 % (cumple); **disc por semilla +0.131, +0.258, −0.077: una semilla supera 0.25** | **NO CUMPLE** |
| V1a | exceso de D_std 0.024, 0.149, 0.600 frente a 0.024, 0.150, 0.600 | cumple |
| V1b | error de D_rob +3.0 %, +3.0 %, +3.2 % | cumple |
| V1c | err_ref con D_rob: 0.0 % (σ = 0.002) y +0.2 % (σ = 0.005); +1.1 % con σ = 0.01 | cumple |
| V2a | razón Dx̂/Dŷ 1.497, 1.993, 4.002 para q = 1.5, 2, 4 | cumple |
| V3 | \|disc\| = 0.056, 0.229, 0.320 con κ = 0.5, 1.0, 1.5 | cumple en el script, **no válido** (ver B0) |
| V4 | \|disc\| = 0.231, 0.599, 0.804 con ε = 0.02, 0.05, 0.10 | cumple en el script, **no válido** (ver B0) |

La regla declarada para B0 decía que, si falla, no se interpreta el resto. Aquí falla solo la parte de disc (el chequeo de consistencia), no la de H. Lo que sigue lo marco como lectura exploratoria cuando depende de disc.

## Por qué falla B0
- re_ac (autocorrelación) por semilla, derivado de los err_ref y disc impresos: ≈ 0.096, 0.083 y 0.115. Dispersión de ±16 % alrededor de 0.098 (media de re_ac = 0.0977, −8 % frente a la referencia; en b8, con 8382 ciclos, salió +9 %).
- re_a0 (hamiltoniano) por semilla: ≈ 0.108, 0.104, 0.106. Dispersión de ±2 %.
- El ruido del chequeo viene de la autocorrelación, no de H. El umbral 0.25 se fijó sin conocer esa dispersión: queda a poco más de una desviación típica de la media de la línea base (disc medio +0.104, \|disc\| medio 0.155). Con tres semillas, 1 de 3 la superó (flag = 0.333).

## V1: ruido de medición (lectura sobre err_ref, que no depende de disc)
| σ (fracción del radio) | D_std/D − 1 | err_ref con D_std | err_ref con D_rob | σ̂ |
|---|---|---|---|---|
| 0.002 | +2.4 % | −0.06 % | +0.02 % | 0 |
| 0.005 | +14.9 % | +2.2 % | +0.2 % | 0.0042 |
| 0.01 | +60 % | **+16.4 %** | +1.1 % | 0.0096 |

- El estimador robusto elimina el efecto del ruido en todo el intervalo probado.
- **No se encontró el punto de ruptura**: con σ = 0.01 (6 % del ancho del ciclo) el error sigue en 1 %. Los niveles probados fueron demasiado bajos para saber hasta dónde aguanta.
- Un D inflado un 60 % da solo +16 % en la tasa de relajación.

## V2: difusión anisotrópica
- Error de H con D isotrópico frente a la verdad anisotrópica: −0.04 %, −3.3 %, −1.2 % (q = 1.5, 2, 4). La frecuencia, < 0.2 %.
- **Esta prueba casi no discrimina:** la tasa de relajación de referencia no cambia con q (0.1065 en los tres casos). Depende solo de la traza de D. Mi expectativa de que el error crecería con q no se cumplió, pero tampoco había por qué esperar sensibilidad de esta cantidad. Queda sin probar si otras partes de la reconstrucción (otros modos, V_FP) resisten la anisotropía.

## V3 y V4 (exploratorio)
| | κ = 0.5 | κ = 1.0 | κ = 1.5 | | ε = 0.02 | ε = 0.05 | ε = 0.10 |
|---|---|---|---|---|---|---|---|
| disc | −0.056 | −0.229 | −0.320 | | −0.231 | −0.599 | −0.804 |
| flag (fracción de semillas) | 0 | 0.33 | 0.67 | | 0 | 1.0 | 1.0 |

La línea base tiene flag = 0.33 y disc medio +0.104.
- **V4:** claramente fuera del ruido de la línea base desde ε = 0.05 (las tres semillas, disc ≈ −0.6). H recupera la tasa del sistema congelado con +8.6 % de error incluso con ε = 0.10, mientras que re_ac se triplica o más (0.27 y 0.59). Sin el chequeo, H daría un resultado de apariencia correcta con datos no estacionarios.
- **V3:** disc crece en módulo con κ y cambia de signo frente a la línea base (+0.10 frente a −0.23 y −0.32). Con κ = 1.0 el flag (0.33) no se distingue de la línea base. Con 3 semillas, no es una detección demostrada.
- `resid_h2` no discrimina: 0.008 a 0.012 en todas las condiciones, 0.009 en la línea base.
- La frecuencia se recupera a < 0.2 % en todas las condiciones con verdad.

## Qué queda por hacer
- Un chequeo de consistencia con incertidumbre propia: intervalo de confianza de re_ac por remuestreo de trayectorias, de modo que valga para un solo conjunto de datos.
- Calibrar su tasa de falsos positivos con más semillas en la línea base, y su potencia en V3 y V4.
- Subir el ruido de medición hasta encontrar dónde se rompe.
