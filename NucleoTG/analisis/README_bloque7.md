# Bloque 7: nulo por nodos y contraste confirmatorio de la señal en u

```bash
cd NucleoTG/analisis
python b7_nulo_nodos.py 50    # vista previa (~10 min)
python b7_nulo_nodos.py       # 400 réplicas, tres valores de h (~1 h)
```

## Qué aporta el notebook 1_b
Solo carga `edge_time_series_normed.csv` y llama a `pk.TemporalNetwork.from_static_network_and_edge_timeseries(..., static_edge_default_weight=1)`. Confirma la convención del cargador: forma (83, 102), 34 aristas temporales y peso 1 en las otras 125. **No muestra cómo se construyeron las series de arista a partir del modelo de Chen**; eso está en otro paso de Phasik que no está en el repositorio.

## Comprobación hecha con los datos (Python puro)
Ajuste de log w_e(t) = c_e + a_u(t) + a_v(t) por mínimos cuadrados en cada instante, con 22 nodos y 34 aristas (la incidencia tiene rango 21 porque la componente BUB2/CDC15/LTE1/TEM1 es bipartita):

| series | R² |
|---|---|
| reales | **0.948** |
| asignadas al azar a las aristas (30 réplicas) | mediana 0.63, rango 0.47–0.73 |

Las series de arista se comportan casi como productos de actividades de nodo. Las aristas que comparten un nodo están correlacionadas por construcción, y los nulos por arista del bloque 5 rompen esa correlación. Por eso pueden ser demasiado permisivos.

## Nulo por nodos
Se estiman las actividades a_i(t), se desplaza cada una con un desfase circular aleatorio y se reconstruyen las aristas con el modelo producto. Este nulo conserva la dinámica de cada nodo y la correlación entre aristas con nodo común; solo destruye la sincronía entre nodos. El observado del contraste es el **modelo** (sin residuo), para comparar lo mismo con lo mismo. También se reportan los estadísticos de los datos reales.

## Predicciones y familias declaradas ANTES de ejecutar
| familia | contrastes | lectura |
|---|---|---|
| confirmatoria | u_max y rango_flujo, h = 0.25, 0.35, 0.5 (Holm sobre 6) | p_holm < 0.05 con los tres h: la señal en u sobrevive y refleja la sincronía entre nodos. Sigue siendo una propiedad de u, la línea base. p_holm ≥ 0.05: la señal del bloque 5 se debía a romper correlaciones que ya venían de la construcción de las series |
| control | rango_bohm1, mismos h | se espera que no sea significativo (como en el bloque 5) |
| secundaria | A_total, coherencia, omega_media_P, h = 0.35 | se espera que no sea significativo |

Sin predicción para la confirmatoria: los dos resultados son plausibles. Requisito previo: el R² que imprime el script debe coincidir con 0.948. Si no coincide, hay un error en la reconstrucción y el resto no se interpreta.
