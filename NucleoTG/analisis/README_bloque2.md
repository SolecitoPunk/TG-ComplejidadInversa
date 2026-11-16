# Bloque 2: diagnóstico de discontinuidades y cierre en Phasik

```bash
cd NucleoTG/analisis
python b2_diagnostico.py      # estimado: 3-6 min
```

Salidas: `resultados/b2_saltos.csv`, `b2_metrica_propia_vs_global.csv`, `b2_cierre_divergencia.csv`.

`phasik.py` reconstruye W[t, i, j] desde los dos archivos en `NucleoTG/`. El pipeline original esperaba `data/kegg/` y `data/chen/`. El estado (log(1+s), C) y el refinamiento temporal son los mismos que en el pipeline original.

## Hechos ya verificados en Python puro (sin numpy)

- Cada serie está dividida por su máximo: max = 1 en las 34 series y ningún mínimo es 0. El mínimo global es 1.7·10⁻⁶.
- **Ningún peso es 0**, así que el grado k_i(t) es constante. La hipótesis «aristas que aparecen o desaparecen» queda descartada antes de ejecutar.
- 7 pares de series son idénticas (por ejemplo CLB6-MBP1 = CLB6-SWI6).
- En el espacio de aristas el ciclo cierra: ‖x(101) − x(0)‖ = 0.152, frente a un paso mediano de 0.128, y τ = 101 es el desfase de mejor recurrencia. t = 101 no repite t = 0.
- Los mayores pasos en el espacio de aristas están en t = 70→71 (‖Δx‖ = 2.34; CLB6-SWI6, CLB6-MBP1 y CLN1-SWI6 bajan 0.84), 0→1, 5→6, 85→86 y 1→2.
- Los nodos del top de saltos tienen aristas temporales con mínimos de ~10⁻⁴: SWI6, MBP1, SWI4 y CLN1 en t = 70; MCM1 a través de CLN3-MCM1 en t = 0. CAK1 no tiene aristas temporales incidentes; se mueve solo por triángulos con vecinos.

## Predicciones declaradas ANTES de ejecutar

| afirmación | apoyo | refutación |
|---|---|---|
| A: `cambio de grado` = 0 | 0 pasos con Δk ≠ 0 | > 0 (indicaría un error en el cargador) |
| B: los saltos son reales en los datos | los mayores `paso_global` están en t = 70→71, 0→1 y 5→6, con causa `salto real de pesos` | dominan pasos sin \|Δw\| grande en ninguna arista relevante |
| B: la métrica original exagera los saltos | MCM1 y LTE1 tienen `paso_propio` ≫ `paso_global` porque su paso mediano propio ≪ el global | el orden y la magnitud no cambian al usar la normalización global |
| B: Onnela amplifica | en saltos dominados por C, `dC_barrat_std` < `dC_onnela_std` y `amp_cbrt` > 1 | Barrat salta igual o más (hipótesis débil; no la daría por segura) |
| C: el cargador nuevo reproduce el original | onnela, ninguna, refine 10, adelante: `indice_cierre` ≈ 3.47 y `div_rel` ≈ 0.60 (la malla de 50 frente a 70 puede mover el segundo decimal) | valores muy distintos: diferencia de carga que hay que resolver antes de seguir |
| C: droplast empeora el cierre | `indice_cierre` mayor que con `ninguna` (el segmento de cierre pasa a ser de 2 pasos) | igual o menor |
| C: periodización lineal | mejora pequeña del índice | gran cambio (la rampa estaría alterando mucho los datos) |
| C: subconjunto | índice menor **por construcción**; no cuenta como evidencia | |
| C: el esquema de punto medio reduce la divergencia | `div_rel_medio` claramente menor que `div_rel_adelante`, sobre todo con refine 10 | iguales |
| C: el resto de la divergencia viene de los saltos | si con medio + refine 10 la divergencia queda ≳ 0.1, la causa son los pasos grandes frente a h, no el esquema | divergencia ≈ 0 con medio + refine 10: entonces el 0.60 original era casi todo error del esquema |

Umbrales fijos (no ajustados): \|Δw\| ≥ 0.3 cuenta como «salto real»; amplificación raíz cúbica > 1 (vale 1/3 cuando w ≈ 1); Barrat/Onnela < 0.3; brecha ≤ 2 pasos medianos para el subconjunto. La regla de causa es un resumen. Las columnas con los valores en bruto están en la tabla para juzgar cada caso.
