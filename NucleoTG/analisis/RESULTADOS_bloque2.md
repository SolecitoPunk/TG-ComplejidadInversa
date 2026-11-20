# Resultados del bloque 2 (ejecutado por el autor)

## Cumplido
- **El cargador reproduce el pipeline original.** Onnela, sin cierre, refine 10, esquema hacia adelante: índice de cierre 3.468 y div_rel 0.6021 (original: 3.47 y 0.602). El salto máximo de 1318 pasos coincide con MCM1 = 1318.
- **Grado constante:** 0 cambios de k. Las «aristas que aparecen o desaparecen» quedan descartadas como causa.
- **Los saltos son reales en los datos.** 11 de los 12 mayores tienen \|Δw\| ≥ 0.3 en una arista relevante: t = 70→71 (SWI6, MBP1, SWI4, CLB6; las aristas CLB6-SWI6/MBP1 y CLN1-SWI6 bajan 0.84), 0→1 y 1→2 (MCM1, LTE1), 5→6 (SWI6), 84→86 (TEM1, LTE1).
- **La métrica «paso propio» exagera los saltos** de los nodos casi inmóviles: TEM1 1.4·10⁵ frente a 293 globales; LTE1 da infinito (paso mediano 0).
- **Descartar el último instante empeora el cierre:** índice 16.4 frente a 3.46.

## Refutado
- **Periodización lineal:** se predijo una mejora pequeña y el índice empeora (13.1). Queda descartada; los datos sin modificar cierran mejor.
- **Punto medio con refine 1:** divergencia peor que hacia adelante (1.20 frente a 0.76). Con saltos mucho mayores que h (\|Δr\| ≈ 1.7 frente a h = 0.35), el anclaje en el punto medio cae en una zona sin densidad. Condición de validez: subpaso máximo < h.
- MCM1 no estaba inflado por la métrica: su salto es real (CLN3-MCM1 baja de 0.42 a 0.007) y la raíz cúbica lo amplifica (amp = 1.35).

## Resultado central: divergencia con punto medio y refine 10
| clustering | div_rel | móviles |
|---|---|---|
| Onnela | 0.079 | 32 |
| Barrat | 0.0042 | 22 |

- La divergencia de 0.60 del pipeline original era casi toda error del esquema y de la discretización. No venía del cierre del ciclo.
- La brecha de cierre no cambia la divergencia (0.0789 con o sin el último instante). El refinamiento periódico rellena el segmento de cierre. Lo que importa es que ese segmento sea plausible, y en el espacio de aristas mide aproximadamente un paso típico.

## Otros hallazgos
- Onnela y Barrat definen estados distintos. El C de Barrat depende solo de los pesos incidentes; el de Onnela también de los pesos entre vecinos. 10 nodos (por ejemplo CAK1) solo se mueven con Onnela. Con Barrat, ΔC en los saltos es de 3 a 6 veces menor (SWI6: 0.12 frente a 0.66).
- Para MCM1 (grado 2, con un triángulo), el C de Barrat vale 1 de forma idéntica. Toda su variación de C con Onnela viene de w^{1/3}.
- **Las trayectorias son mesetas con saltos:** paso mediano global 0.0034 frente a saltos de ~1.7. La corriente se concentra en pocos segmentos que cruzan zonas de densidad baja.
- 20 de 34 series bajan de 10⁻³.
- Error corregido: `paso_global_barrat` usaba la mediana de los nodos móviles con Onnela. Ahora usa los de Barrat.

## Decisiones para el bloque 3 (derivadas del diagnóstico)
- Estado principal: **Barrat**; Onnela como análisis de sensibilidad. Motivo: la condición estacionaria se cumple con Barrat (div 0.004) y no tanto con Onnela (0.08), y Barrat es lineal en los pesos.
- Cierre: `ninguna`.
- Corriente: punto medio con TIME_REFINE ≥ 10, verificando subpaso máximo < h.
