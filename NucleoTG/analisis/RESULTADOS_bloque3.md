# Resultados del bloque 3 (ejecutado por el autor)

## Cumplido
- Barrat, referencia: subpaso máximo 0.73·h y div_rel 0.0042 (igual que el bloque 2).
- La máscara pierde corriente con Barrat: conserva el 95.5 % de la masa de P pero solo el 53 % de la de J (predicción < 0.5; cumplida en lo cualitativo, justo en el límite).
- Mínimos más persistentes junto a nodos estáticos: U 0.75 (3 de los 4 existentes), V_B 0.8 (Barrat); 0.8 / 0.8 (Onnela).
- V_B tiene más mínimos que U: 12 frente a 4 (Barrat), 11 frente a 5 (Onnela). Relevantes: 9 frente a 4 y 7 frente a 3.
- Con λ ≥ 0.1, V da los mismos mínimos que V_B (fracción 1).
- Γ_propio está sesgado: SWI5 (Barrat) 14.7 frente a Γ_loo 0.53.

## Refutado
- **El flujo no es despreciable con Barrat:** rango(flujo)/rango(Bohm) = 0.16 con λ = 1 (predicción ~10⁻²). Con Onnela es 0.0013. El «flujo despreciable» del pipeline original era propio de Onnela y del esquema hacia adelante.
- Con Onnela la máscara conserva el 88 % de J, y con refine 10 el subpaso máximo es 1.27·h (viola la condición). **Onnela requiere refine 20** (0.81·h).
- Con Onnela, λ pequeño no cambia los mínimos: V(λ = 0.001) sigue emparejando 1.0 con V_B.

## No concluyente: estabilidad de V_B frente a U
- Fracción media emparejada: Barrat U 0.81 / V_B 0.85; Onnela 0.85 / 0.85. La diferencia equivale a un mínimo.
- Refine 5 o 20 no cambia nada (fracción 1 en todos los campos). Solo h discrimina, con resultado mixto: Barrat h = 0.25 U 0.5 / V_B 0.8; h = 0.5 U 0.75 / V_B 0.6.
- **Sesgo de la prueba:** un campo con más mínimos tiene más candidatos para emparejarse por azar (V_B 12 frente a U 4). Falta una tasa de referencia por azar (se añadirá en el bloque 6).

## λ pequeño
Con Barrat y λ ≤ 0.01 el número de mínimos relevantes de V cae a 1. El término −½\|u\|² crea un único pozo donde \|u\| es máximo. Esa información ya está en u, que es parte de la línea base.

## Circulación
| | A_total | Σ\|A\| | coherencia | lazo mayor |
|---|---|---|---|---|
| Barrat | +0.54 | 1.74 | 0.31 | SWI5, A = +0.82 |
| Onnela | −0.09 | 1.15 | 0.08 | SWI5, A = **−0.21** |

- **El sentido de rotación de SWI5 depende de la definición de C.** Con Onnela y con Barrat, el clustering de SWI5 cambia en fases distintas respecto a su fuerza. El sentido del flujo en este plano no es una propiedad invariante de los datos.
- MBP1 (Barrat): Γ_loo = 0.525 ≈ Γ_propio = 0.54. Otros nodos (SWI4 y SWI6, con series compartidas) recorren el mismo lazo. Es el único caso de flujo colectivo en la tabla.
