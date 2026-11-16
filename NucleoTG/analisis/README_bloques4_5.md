# Bloques 4 y 5: separación estático/dinámico y modelos nulos

```bash
cd NucleoTG/analisis
python b4_separacion.py        # estimado: 2-4 min
python b5_nulos.py 50          # prueba rápida (~5 min)
python b5_nulos.py             # 400 réplicas por nulo (estimado: 25-40 min)
```

Cambios de infraestructura:
- `campos.densidad_kde` acepta `pesos` y `corriente_kde` acepta `n_total`. `comunes.campos_rapidos` usa ambos para tratar cada nodo estático como un punto de peso T. El bloque 4 comprueba que coincide con el cálculo directo.
- El triángulo de Onnela se calcula con `R @ R`, que es algebraicamente idéntico y más rápido.
- Con Onnela se usa refine 20, porque con refine 10 el subpaso supera h (bloque 3).

## Predicciones del bloque 4 (declaradas antes de ejecutar)

| afirmación | apoyo | refutación |
|---|---|---|
| El cálculo rápido es exacto | diferencia relativa ≲ 1e-10 | mayor (error en `comunes.py`) |
| Los mínimos más persistentes de U en 'todos' vienen de los estáticos | `frac_en_estaticos` de U ≥ 0.75 y > `frac_en_moviles` | lo contrario |
| Lo mismo para V_B | `frac_en_estaticos` de V_B ≥ 0.75 | < 0.5 |
| Los estáticos diluyen u | `u_max_en_mascara` y `flujo_sobre_bohm_l1` mayores en 'moviles' que en 'todos' | iguales o menores |
| V_B de los estáticos tiene un mínimo por cada grupo aislado | `nmin_V_B` (estáticos) ≈ `aisladas_mas_de_h` + grupos sin aislar resueltos | muy distinto (sin un mecanismo claro) |

## Predicciones del bloque 5

| afirmación | apoyo | refutación |
|---|---|---|
| Inversión temporal | A_total y omega_media_P cambian de signo; el resto igual (precisión de máquina) | cualquier otra cosa (error de código) |
| ¿La circulación es más coherente de lo esperado? | **sin predicción**. Si `coherencia` o `A_total` tienen p_holm < 0.05 frente a **ambos** nulos, hay rotación colectiva no explicada por las series individuales | p_holm ≥ 0.05: la circulación observada es la típica de series desordenadas |
| Peso del flujo | **sin predicción** para `flujo_sobre_bohm_l1`; se compara con los nulos para ver si el valor observado es especial | |
| Lectura | un resultado significativo con Barrat y no con Onnela (o al revés) **no** se puede leer como propiedad de la red: depende de la definición de C (bloque 3: SWI5 cambia de signo) | |

Diseño de contrastes (corregido antes de ejecutar):
- En la primera versión, con 200 réplicas y Holm sobre 16 contrastes, el p_holm mínimo alcanzable era 16 × 2/201 ≈ 0.16. Ningún resultado habría podido ser significativo.
- Ahora la **familia primaria** se declara de antemano: A_total, coherencia y omega_media_P, frente a 2 nulos (6 contrastes por clustering). Con 400 réplicas, el p_holm mínimo es 0.03. La familia secundaria es exploratoria y se corrige por separado.
- Los nulos cambian también P, así que solo se contrastan estadísticos globales, no mapas punto a punto.
- Con Onnela solo hay estadísticos sin kernel; su familia primaria tiene 4 contrastes.
