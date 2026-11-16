# Resumen final: bloques 1-6

Pregunta de la línea 2: con los mismos datos, ¿la representación de Madelung–Bohm con flujo (V = λ·V_B − ½|u|²) aporta algo medible frente a la línea base (U = −ln P̄ y u medido)?

**Respuesta con estos datos y estas elecciones: no.**
- Los mínimos de V_B no son más estables que los de U una vez corregido el emparejamiento por azar.
- Con λ ≥ 0.1, V tiene los mismos mínimos que V_B. Con λ pequeño, V tiene menos mínimos estables.
- Lo único que distingue los datos de los modelos nulos está en u (línea base). El término de Bohm de los datos es típico de los nulos.
- V es invariante bajo inversión temporal por construcción, así que no puede ver el sentido de rotación.

Es un resultado negativo, y es válido.

## Bloque 5 con 400 réplicas (Barrat, h = 0.35)

| estadístico | familia | p (desfase / permutación) | p_holm | lectura |
|---|---|---|---|---|
| A_total, coherencia, omega_media_P | primaria | ≥ 0.34 / ≥ 0.34 | 1 | sin rotación colectiva; coherencia 0.31 frente a una mediana nula de 0.52–0.54 |
| Onnela: A_total, coherencia | primaria | ≥ 0.20 | ≥ 0.80 | igual |
| flujo_sobre_bohm_l1 | secundaria | 0.005 / 0.005 | 0.0499 | supera a las 400 réplicas; justo en el umbral (p_holm mínimo posible = 0.0499) |
| u_max_mascara | post hoc | 0.005 / 0.005 | 0.030 | supera a las 400 réplicas |
| rango_flujo | post hoc | 0.005 / 0.005 | 0.030 | supera a las 400 réplicas |
| rango_bohm1 | post hoc | 0.28 / 0.87 | 0.56 / 0.87 | **típico de los nulos** |

Inversión temporal: exacta (A_total y omega_media_P cambian de signo; \|u\|², P y V no cambian).

## Bloque 6

**Estabilidad de mínimos corregida por azar** (media sobre h = 0.25 y 0.5):

| campo | Barrat: emparejados / azar / exceso | Onnela: emparejados / azar / exceso |
|---|---|---|
| U | 0.62 / 0.11 / **0.51** | 0.70 / 0.12 / **0.58** |
| V_B (= V con λ ≥ 0.1) | 0.70 / 0.14 / **0.56** | 0.70 / 0.14 / **0.56** |
| V(λ = 0.003) | 0.50 / 0.14 / 0.36 | 0.70 / 0.14 / 0.56 |

La diferencia entre U y V_B (±0.05) es menor que un mínimo de 5. Refine 5 a 40 no mueve ningún mínimo.

**Sensibilidad** (predicciones del README_bloque6):
- ✓ div_rel y masa_J varían < 2 % entre mallas de 40, 60 y 80. Los estadísticos basados en máximos o rangos (u_max, flujo/Bohm) varían entre un 10 % y un 30 % con la malla: dependen de los valores extremos que caen en ella.
- ✓ nrel_V_B crece al bajar h (Barrat: 3, 9, 12 para h = 0.5, 0.35, 0.25).
- ✓ A_total no depende de h ni de la malla (0.5395). Con refine varía en el cuarto decimal, como se espera de un polígono más fino.
- Cociente flujo/Bohm frente a h:
  - ✓ Barrat: crece (0.027, 0.16, 0.21).
  - ✗ **Onnela: decrece** (0.0027, 0.0013, 0.0005). En Onnela el flujo vive en corredores estrechos y el suavizado lo borra más rápido de lo que el término de Bohm baja como 1/h².

## Tabla resumen

| # | pregunta | prueba | resultado | estado |
|---|---|---|---|---|
| 1 | ¿El pipeline recupera soluciones conocidas? | rotación, OU, Fock–Darwin | sí: identidad a 1e-13; OU radial 0.001 (medio) frente a −0.99 (adelante); FD de orden 2 | establecido |
| 2 | ¿Qué esquema de corriente? | OU y Phasik | punto medio, con la condición subpaso < h; el esquema hacia adelante duplica \|u\|² con ruido | establecido |
| 3 | ¿Inverso de FD con ruido? | 1c | error ≈ 1.1·ε/dx², crece al refinar; la forma √P es mejor que la forma P | establecido |
| 4 | ¿Causa de los saltos en Phasik? | 2 | saltos reales de pesos (t = 70→71 y otros); grado constante; Onnela amplifica cerca de w = 0 | establecido |
| 5 | ¿El ciclo cierra? | 2 | sí en el espacio de aristas; la div_rel de 0.60 era error del esquema (Barrat + punto medio: 0.004); droplast y lineal empeoran | establecido |
| 6 | ¿El flujo es despreciable frente a Bohm? | 3, 6 | depende de C y de h: Barrat 0.03–0.21, Onnela 0.0005–0.003 (λ = 1) | establecido (depende de la definición) |
| 7 | ¿V_B localiza mínimos más estables que U? | 3, 6 | no: exceso sobre el azar 0.56 frente a 0.51 (Barrat), 0.56 frente a 0.58 (Onnela) | establecido para esta prueba (resolución: un mínimo de 5) |
| 8 | ¿V añade algo a V_B? | 3, 6 | con λ ≥ 0.1, mismos mínimos; con λ pequeño, un pozo donde \|u\| es máximo y menor estabilidad | establecido |
| 9 | ¿Los mínimos son estructura estática? | 3, 4 | en parte: alrededor de la mitad viene de estáticos, una cuarta parte de móviles y el resto de la combinación | establecido |
| 10 | ¿Hay rotación colectiva? | 3, 5 | no frente a ninguno de los dos nulos; el sentido de rotación de SWI5 cambia entre Barrat y Onnela | establecido (negativo) |
| 11 | ¿Algo distingue los datos de los nulos? | 5 | sí, pero solo en u: u_max y rango_flujo superan a las 400 réplicas; rango_bohm1 no | **sugerido** (post hoc) |
| 12 | ¿Por qué u_max es alta? | — | hipótesis: SWI4, SWI6 y MBP1 son adyacentes y saltan juntos en t = 70 | no concluyente |
| 13 | ¿Los mínimos aislados de los estáticos desaparecen por la máscara? | 4 | hipótesis no verificada | no concluyente |

## Conclusiones

**Establecido**
1. El pipeline está validado con soluciones conocidas, con dos condiciones explícitas: corriente con esquema de punto medio y subpaso < h.
2. En Fock–Darwin, el método inverso converge con orden 2 con datos exactos. Con ruido está mal condicionado (error ∝ ε/dx²) y requiere regularización. La forma √P del término de Bohm es la que conviene usar. El error puntual cerca del nodo r = 0 no converge.
3. Los problemas del pipeline original en Phasik (divergencia 0.60, flujo «despreciable», ciclo que «no cierra») eran artefactos del esquema hacia adelante y de la métrica de pasos. Los saltos sí son reales en los datos.
4. V_B no localiza mínimos más estables que U, y V no mejora a V_B. V es invariante bajo inversión temporal, así que no distingue el sentido del flujo.
5. No hay rotación colectiva distinguible de los nulos. El sentido de rotación en el plano (s, C) depende de la definición de C.

**Sugerido**

6. La velocidad media máxima en la región densa (u_max, rango_flujo) es mayor que en todas las réplicas de ambos nulos (Barrat, h = 0.35; p_holm = 0.03, post hoc). El término de Bohm de los datos es típico de los nulos. **Si la señal se confirma, pertenece a la línea base, no a la representación de Bohm.**
   - Es post hoc: se eligió tras ver el resultado de 50 réplicas.
   - Solo se probó con Barrat y h = 0.35.
   - Los estadísticos de máximo dependen un 10–30 % de la malla.
   - Si Phasik construye las series de arista a partir de concentraciones de nodo, las aristas que comparten un nodo están correlacionadas por construcción. En ese caso, los nulos por arista son demasiado permisivos y el nulo adecuado es por nodo. No pude comprobarlo: el notebook `1_b` no está en el repositorio.

**No concluyente**

7. El mecanismo de 6 (co-movimiento de SWI4, SWI6 y MBP1).
8. Cualquier lectura biológica de los mínimos o barreras: no se probó, y la analogía no la autoriza.
9. Por qué con Onnela el cociente flujo/Bohm decrece con h.

## Supuestos de la analogía (no son mecanismo biológico)
- P̄ y J̄ son la densidad y la corriente de estados de nodo en un plano construido (log(1+s), C). No representan ninguna probabilidad de un sistema físico.
- La continuidad estacionaria se cumple porque las trayectorias son cerradas, no por una ley de conservación.
- λτ² es un parámetro libre. Con λτ² ≥ 0.1, V es en la práctica V_B.
- Las 125 aristas sin serie reciben peso 1 (convención de Phasik). Cada serie está normalizada por su máximo, así que los pesos no son comparables entre aristas.

## Siguientes pasos posibles (solo si se quiere seguir con la línea 2)
1. Confirmar la observación 6 con un contraste declarado de antemano: u_max frente a nulos con h = 0.25 y 0.5, sin tocar nada más.
2. Un nulo por nodo (desfase de las concentraciones de nodo y reconstrucción de las aristas). Requiere el notebook `1_b`.
3. Replicar con datos independientes (RNA-seq, notebook `2_a`; ratón, `4_a`). Es la única confirmación que no reutiliza los mismos datos.
