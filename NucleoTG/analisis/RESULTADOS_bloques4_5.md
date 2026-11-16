# Resultados de los bloques 4 y 5 (bloque 5 preliminar, 50 réplicas)

## Bloque 4
- Cálculo rápido frente a directo: diferencia de 3·10⁻¹³ (Barrat) y 6·10⁻¹³ (Onnela). ✓
- Estáticos: Barrat 61 nodos en 22 posiciones distintas (13 aisladas a más de h); Onnela 51 en 16 (14 aisladas). Hasta 13 nodos comparten una misma posición.
- **Los estáticos diluyen u** ✓:

  | | u_max (todos → móviles) | flujo/Bohm, λ = 1 (todos → móviles) |
  |---|---|---|
  | Barrat | 1.68 → 3.90 | 0.16 → 0.82 |
  | Onnela | 0.15 → 0.34 | 0.0013 → 0.0072 |

- **Refutado:** los mínimos más persistentes de «todos» no son mayoritariamente estáticos. U: 0.5 estáticos / 0.25 móviles (Barrat), 0.6 / 0.2 (Onnela). V_B: 0.6 / 0.4 en ambos. Los mínimos son una mezcla, y algunos solo aparecen al combinar ambas poblaciones. El 0.75–0.8 del bloque 3 medía cercanía a posiciones estáticas, no coincidencia con los mínimos del campo de solo estáticos.
- **Refutado:** V_B de los estáticos tiene menos mínimos que grupos aislados (10 frente a 13; 9 frente a 14). Hipótesis no verificada: un nodo aislado da un pico de ~1/13 del máximo, cerca del umbral del 5 %; su vecindad toca el borde de la máscara y el mínimo se descarta.
- Solo móviles (Barrat): con λ ≤ 0.01, V no tiene ningún mínimo relevante (el término de flujo domina el rango).

## Bloque 5 (50 réplicas)
- Inversión temporal: exacta (A_total y omega_media_P cambian de signo; el resto, idéntico). ✓
- **Primarios: nada significativo** (p brutos ≥ 0.27). La coherencia observada (0.31) está por debajo de la mediana de los nulos (0.52 desfase, 0.54 permutación). No hay rotación colectiva más allá de la que dan series desordenadas, con ninguna de las dos definiciones de C.
- **Secundario, exploratorio:** el cociente flujo/Bohm observado (0.171) supera a las 50 réplicas en ambos nulos (medianas 0.044 y 0.033; z ≈ 5). p = 0.039, que es el mínimo posible con 50 réplicas; p_holm = 0.39.
- Hipótesis: SWI4, SWI6 y MBP1 son adyacentes y saltan juntos en t = 70, así que sus velocidades se suman en el mismo corredor. Ambos nulos rompen esa coincidencia.
- Siguiente paso: 400 réplicas con u_max, rango_flujo y rango_bohm1 (familia post hoc, declarada como tal) para saber si la señal está en u (línea base) o en P.
