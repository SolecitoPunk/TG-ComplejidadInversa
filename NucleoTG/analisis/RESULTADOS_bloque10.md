# Resultados del bloque 10 (versión corregida; ejecutado por el autor)

## Criterios declarados
| id | resultado | estado |
|---|---|---|
| C1 'rota' significativo | p = 0 (400 réplicas), A = 4.87 | cumple |
| C2 'no_rota' no significativo | p = 0.965, A = 0.007 | cumple |
| C3 \|vort(rota)\| > 3·\|vort(no_rota)\| | 8.71 frente a 0.021 | cumple |
| C4 0.1 ≤ flujo/Bohm ≤ 10 en 'rota' | **41.6** (D_hat = 0.266) | **NO CUMPLE** |
| C5 'rota' es el que más gira | A_norm: rota 0.894, debil 0.635, no_rota 0.002, anti_fase 0.000 | cumple |
| C6 'anti_fase' no significativo | p = 0.965 | cumple |

El detector geométrico de rotación (área con signo, vorticidad, nulo de desfase) funciona: distingue rotación de su ausencia, sin falsos positivos, y respeta la física del desfase (máximo en cuadratura, nulo en fase y en oposición).

## Por qué falla C4: el modelo no tiene difusión
Comprobación en Python puro, con el mismo modelo y el mismo estimador:

| escenario | D_hat con ruido de observación (5 %) | D_hat sin ruido de observación |
|---|---|---|
| rota | 0.262 | 0.096 |
| no_rota | 0.263 | 0.100 |
| anti_fase | 0.248 | 0.098 |

- D_hat es igual en los cuatro escenarios. Unas dos terceras partes vienen del ruido de observación (el efecto que el bloque 9 midió), y el resto de la curvatura de la curva determinista muestreada a 24 puntos por día.
- **El modelo no contiene una difusión en el sentido de Fokker–Planck.** La variación de un día a otro es un factor de escala aleatorio constante en todo el día (desorden «congelado»), no un ruido que actúe dentro de la dinámica. D_hat no mide nada físico y λ = 2·D_hat no tiene significado.
- El valor 41.6 no es necesariamente un error de unidades: con \|u\| ≈ 20 y la escala del kernel, el cociente se comporta como un número de Péclet al cuadrado. Pero como D_hat no es una difusión, el número tampoco es interpretable. El criterio C4 queda NO CUMPLIDO y no se reformula.

## El hallazgo principal: un sistema forzado por el reloj
Autocorrelación de la fase z/\|z\| en la serie de días concatenados (escenario 'rota'):

| desfase | 1 día | 5 días | 20 días | 100 días |
|---|---|---|---|---|
| \|C\| | 0.974 | 0.977 | 0.974 | 0.974 |

La fase no se decorrelaciona nunca, porque la marca el reloj: las 8 h son siempre las 8 h. El sistema es un **oscilador forzado**, no un ciclo límite autónomo. Consecuencias:
- No hay difusión de fase, así que la predicción del bloque 8 (la tasa de relajación del primer modo oscilatorio debe coincidir con el decaimiento de la autocorrelación) no se aplica: no hay decaimiento que predecir.
- Con forzamiento periódico, el proceso es cicloestacionario. La densidad en el plano 2D es un promedio sobre la fase del día, no el estado estacionario de un operador de Fokker–Planck con deriva independiente del tiempo. La reformulación del documento de teoría supone lo segundo.
- Esto describe también, con alta probabilidad, los datos reales de bicicletas (y en general los ciclos sociales marcados por el calendario: tráfico, cafés, consumo). Es una afirmación por razonamiento, no comprobada con los datos reales.

## Qué queda establecido
- **Caso (a), geométrico:** área, vorticidad y circulación detectan la rotación de forma fiable en un sistema tipo bicicletas. Es la parte que pertenece a la línea base, no al término de Bohm.
- **Caso (c), espectral:** no aplica a sistemas forzados por el reloj sin una extensión de la teoría (por ejemplo, Fokker–Planck con deriva periódica en el tiempo y teoría de Floquet), que **no está derivada**.
- Para la lista de «dónde aporta y dónde no»: los sistemas forzados por un reloj externo quedan del lado de «no aplica la versión estacionaria».

## Corrección registrada
En el bloque 10 original llamé al cociente 124 «error de unidades». Lo era, en parte (D_hat sin unidades de difusión). En esta versión el estimador tiene las unidades correctas y el problema es más profundo: el modelo no tiene la difusión que el estimador supone medir.
