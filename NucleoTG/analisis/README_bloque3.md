# Bloque 3: línea base (U, flujo) frente a V_Bohm y V completo

```bash
cd NucleoTG/analisis
python b3_linea_base.py      # estimado: 4-8 min
```

Salidas: `resultados/b3_configuraciones.csv`, `b3_estabilidad.csv`, `b3_lambda.csv`, `b3_circulacion.csv`.

## Definiciones

- **Campos:** U = −ln P̄; V_B = término de Bohm por unidad de λ (sus mínimos no dependen de λ); V(λ) = λ·V_B − ½\|u\|². Aquí λ = λτ² es el único parámetro libre.
- **Mínimos y barreras:** persistencia de los conjuntos de subnivel (unión-búsqueda, 8 vecinos, solo dentro de la máscara). La barrera de un mínimo es la altura del punto de silla por el que su cuenca se une a una más profunda, menos su valor. Se reporta relativa al rango del campo. Se descartan los mínimos que tocan el borde de la máscara. La lógica se comprobó en Python puro con dos pozos de barrera conocida (persistencia 0.400 frente a 0.4 analítica).
- **Estabilidad:** de los 5 mínimos más persistentes de la referencia (h = 0.35, refine 10), fracción que tiene pareja entre los 5 de la configuración perturbada a menos de 0.35. Perturbaciones: h = 0.25 y 0.5; refine = 5 y 20.
- **Circulación:**
  - A_i: área con signo del lazo de cada nodo, sin kernel. Antihorario es positivo.
  - Coherencia: \|ΣA_i\| / Σ\|A_i\|. Vale 1 si todos los nodos giran en el mismo sentido.
  - Γ = ∮u·dl y Φ = ∮J·dl / L (análogo al de Wang), sobre los 5 lazos de mayor \|A_i\|.
  - Versión `propio`: está **sesgada a positivo**, porque la velocidad del propio nodo se alinea con dl.
  - Versión `loo`: excluye al nodo del lazo y mide si los demás nodos fluyen a lo largo de él. Γ_loo es poco fiable donde no hay otros nodos cerca (P_loo ≈ 0); Φ_loo no tiene ese problema.

## Predicciones declaradas ANTES de ejecutar

| afirmación | apoyo | refutación |
|---|---|---|
| Validez del esquema | `subpaso_max_sobre_h` < 1 con refine ≥ 10; div_rel (Barrat, ref) ≈ 0.004 como en el bloque 2 | > 1 o div_rel muy distinta |
| **La máscara del 5 % elimina la corriente** | `masa_J_en_mascara` claramente menor que `masa_P_en_mascara` (por ejemplo < 0.5 frente a > 0.8) | `masa_J_en_mascara` ≳ 0.8 |
| El término de flujo es pequeño dentro de la máscara | `rango_flujo_sobre_bohm_l1` ~ 10⁻² o menor (con Onnela el pipeline original daba 0.003) | ≳ 0.3 |
| **Los mínimos más persistentes de U y V_B son estructura estática** | `top_cerca_estatico_U` y `_V_B` ≥ 0.8 | < 0.5 |
| V_B amplifica estructura fina | `nmin_V_B` > `nmin_U` y `nrel_V_B` ≥ `nrel_U` | `nmin_V_B` ≤ `nmin_U` |
| V_B no es más estable que U | `frac_emparejados` de V_B ≤ la de U (promedio sobre perturbaciones) | V_B claramente más estable que U |
| λ grande ⇒ V ≈ V_B | V(l=1) y V(l=0.1): `frac_en_top_V_B` ≈ 1 | < 0.6 |
| λ pequeño cambia los mínimos | V(l=0.001): `frac_en_top_V_B` bajo | ≈ 1 en todo el rango |
| V(λ pequeño) es menos estable | `frac_emparejados` de V(l=0.001) < la de V_B | igual o mayor |
| Circulación | **sin predicción de signo ni de valor.** Solo: Γ_propio > 0 por el sesgo; \|Γ_loo\| ≪ Γ_propio si los lazos no se solapan; el significado de la coherencia se decide en el bloque 5 contra modelos nulos | |

Si V_B resulta más estable que U, eso sería evidencia a favor de la representación de Bohm. Si resulta igual o menos estable, y sus mínimos coinciden con los de U, la conclusión es que no aporta nada frente a la línea base para localizar mínimos.
