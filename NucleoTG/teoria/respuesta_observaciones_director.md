# Respuesta a las observaciones del director (versión 2 del anteproyecto)

| # | Observación | Cambio en `propuesta_trabajo_grado.tex` |
|---|---|---|
| 1 | Título demasiado extenso | Se adoptó el título propuesto: «Análisis del problema inverso de la ecuación de Schrödinger estacionaria con potencial vectorial: formulación hidrodinámica y estudio de estados de Fock–Darwin». |
| 2 | Estado del arte como historia científica, con el vacío surgiendo de la comparación | La sección e se reescribió en seis etapas: espectral 1D, dispersión, magnético, estado fundamental, hidrodinámica y Fock–Darwin. Cada etapa indica su aporte y su límite, y al final hay una tabla comparativa de la que sale el vacío. La sección c resume esa trayectoria antes de formular la pregunta. |
| 3 | Delimitación física del problema | Tabla con sistema físico, modelo, objeto de estudio y magnitudes. Segunda tabla con datos, incógnitas y qué se determina según los datos disponibles: (P, j), (P, S), (P, S, B_z) y (P, S, V). |
| 4 | Pregunta científica | Se adoptó la pregunta propuesta. |
| 5 | Objetivos | Se adoptaron el objetivo general y los cuatro específicos propuestos (OE1–OE4). |
| 6 | Marco teórico: distinguir lo establecido, lo reportado y lo propuesto | Cada subsección lleva una etiqueta: [Establecido], [Literatura] o [Propuesto]. También se explicitan las hipótesis: partícula sin espín, ψ de clase C² fuera de un conjunto nodal de medida nula, decaimiento en el infinito. |
| 7 | Fase documental explícita; verificación computacional acotada | Nueva Fase 1 con criterios de búsqueda (bases y cadenas), bola de nieve, inclusión y exclusión, matriz de clasificación y comparación. El estudio computacional se reduce a tres estados de Fock–Darwin, (0,0), (0,1) y (1,0), con un solo cociente ω_c/ω₀ = 2. Se eliminaron los barridos y las geometrías generales. |
| 8 | Cronograma alineado | Cada actividad del cronograma está asociada a un objetivo (OE1–OE4). |
| 9 | Ampliar la bibliografía | Se añadieron referencias sobre problemas inversos espectrales y de dispersión, problemas inversos magnéticos, la construcción supersimétrica, la formulación hidrodinámica y el efecto Aharonov–Bohm. Las que no se han verificado contra la fuente llevan la marca †. |

## Decisiones que conviene confirmar
- **Barad y Latour.** Las recomendaciones del director no los mencionan, y su título, su pregunta y sus objetivos no los incluyen. Quedaron como una «dimensión reflexiva» de un párrafo en la justificación y como cierre del documento, sin objetivo propio. Si el director prefiere quitarlos o darles un capítulo, se ajusta.
- **Corriente de probabilidad como dato.** Al delimitar las magnitudes (punto 3) se obtuvo un resultado útil. Con datos invariantes de gauge (P, j), el campo magnético y el potencial escalar quedan determinados fuera de los nodos. Se comprobó en Fock–Darwin (0,1), con B_z reconstruido = 2.000000. La falta de unicidad aparece cuando se usa la fase S, que depende del gauge. Esto conecta con los resultados clásicos de unicidad salvo gauge (Sun, Nakamura–Sun–Uhlmann, Eskin–Ralston).
- **Correspondencia con Fokker–Planck.** Quedó fuera del anteproyecto para respetar el alcance.
