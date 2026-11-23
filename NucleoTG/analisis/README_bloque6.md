# Bloque 6: barridos y estabilidad corregida por azar

```bash
cd NucleoTG/analisis
python b5_nulos.py      # 400 réplicas, ahora con la familia post hoc (25-40 min)
python b6_barridos.py   # 5-10 min; Onnela con refine 40 usa ~0.5 GB de RAM
```

## Predicciones declaradas ANTES de ejecutar

**Bloque 5 con 400 réplicas (familia post hoc: u_max, rango_flujo, rango_bohm1)**

| resultado | lectura |
|---|---|
| `u_max_mascara` o `rango_flujo` con p bajo y `rango_bohm1` no | la señal está solo en u (línea base). La representación de Bohm no añade información para detectarla |
| solo `rango_bohm1` con p bajo (P más plana en los nulos) | el cociente es alto porque los nulos producen una P con más curvatura; no es una señal de flujo |
| ninguno con p bajo, y el cociente sí | la señal aparece solo en la combinación. Sería el único caso a favor de V; requiere confirmación |
| el cociente deja de superar a las réplicas con 400 | el valor de 50 réplicas fue azar |

Mi expectativa (no es una prueba): la primera fila, porque el bloque 4 mostró que \|u\| cambia mucho al quitar los estáticos mientras V_B cambia poco.

**Bloque 6**

| afirmación | apoyo | refutación |
|---|---|---|
| Parte de la estabilidad de V_B era azar | `azar` de V_B > `azar` de U | iguales |
| V_B no es más estable que U tras corregir | `exceso` de V_B ≤ `exceso` de U + 0.1 | `exceso` de V_B claramente mayor (sería evidencia a favor de Bohm) |
| div_rel y masa_J dependen poco de la malla | variación < 10 % entre mallas de 40, 60 y 80 | mayor (las derivadas analíticas no deberían depender de la malla) |
| `nrel_V_B` crece al bajar h | más mínimos con h = 0.25 que con 0.5 | lo contrario |
| `flujo_sobre_bohm_l1` crece con h | el término de Bohm escala como ~1/h² (bloque 1) | decrece |
| A_total no depende de h ni de la malla | constante (se calcula sin kernel) | varía (error) |
