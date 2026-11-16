# Bloque 10: sintético de bicicletas compartidas (viabilidad antes de datos reales)

```bash
cd NucleoTG/analisis
python b10_bicis_sintetico.py     # estimado: 4-8 min
```

## Qué prueba y qué NO prueba
Prueba si el estado 2D de un sistema tipo bicis (salidas, llegadas) por hora tiene un **flujo rotacional separable del ruido**, que es la condición previa para que la ecuación de Madelung–Bohm aporte algo. **No** es todavía la prueba espectral falsable del bloque 8: eso requiere la parte del hamiltoniano y vendría después, solo si este bloque y los datos reales lo justifican.

## Modelo
El "día" es el ciclo; se repite ND = 300 veces con ruido de día a día (σ = 0.20) y ruido de observación (0.05). Cada día es una curva cerrada de 24 h en el plano (salidas, llegadas) estandarizado. El conjunto de días es el ensemble para estimar densidad, corriente y difusión.

Cuatro escenarios, parametrizados por el desfase entre los dos picos como fracción del ciclo. **El giro es máximo en cuadratura (1/4 de ciclo), no en oposición de fase.** Con perfiles simétricos, en fase (0) y en oposición (1/2) la curva va y vuelve por la misma recta y no gira:
- **rota**: 1/4 de ciclo (picos a 5 h y 11 h). Cuadratura, giro máximo.
- **debil**: 1/16 de ciclo. Casi en fase.
- **no_rota**: 0. En fase.
- **anti_fase**: 1/2 de ciclo. Oposición de fase; control de que el máximo no está ahí.

Verificado en Python puro (área normalizada por el radio, 1 = círculo): rota 0.89, debil 0.64, no_rota −0.01, anti_fase 0.00.

> **Corrección de diseño (primera versión).** La primera versión fijaba `rota` en medio ciclo (12 h) y daba área casi nula, y usaba un estimador de D sin unidades de difusión (media varianza del área), que producía un cociente flujo/Bohm absurdo (124). Ambos están corregidos: desfases por la física de la cuadratura, y D estimada por segundas diferencias en el plano de estados (bloques 8-9).

## Criterios declarados ANTES de ejecutar
| id | condición | si falla |
|---|---|---|
| C1 | 'rota' tiene rotación significativa frente al nulo (p < 0.05) | el detector de rotación no sirve |
| C2 | 'no_rota' NO es significativo (p ≥ 0.05) | **falso positivo**: el método inventa rotación donde no la hay; descalifica el pipeline para datos reales |
| C3 | \|vorticidad(rota)\| > 3·\|vorticidad(no_rota)\| | la vorticidad con kernel no separa los casos |
| C4 | el flujo aporta en 'rota' y en rango sensato (0.1 ≤ flujo/Bohm ≤ 10) | marginal (ecuación no aporta) o absurdo (error de escala en D) |
| C5 | 'rota' (cuadratura) es el que más gira en \|área normalizada\| | el detector no respeta la física del desfase |
| C6 | 'anti_fase' (oposición) NO es significativo | el máximo de rotación estaría mal ubicado |

El modelo nulo desfasa en el tiempo el eje de llegadas de cada día, lo que destruye la relación temporal entre los dos ejes conservando cada perfil. 400 réplicas, p bilateral.

## Qué significa cada resultado
- **C1 y C2 se cumplen:** el pipeline distingue rotación real de su ausencia, sin falsos positivos. Es el requisito mínimo para pasar a datos reales.
- **C2 falla:** el método marca rotación en un sistema que no gira. Habría que entender por qué antes de tocar datos reales (sería el análogo del artefacto de kernel que vimos en Phasik).
- **C4 se cumple:** en un sistema que gira con ruido realista, el término de flujo no es despreciable frente al de Bohm con λ = 2D. Esto es lo contrario de lo que pasó con Phasik (λ libre, flujo ~0.5 %), y sería la primera señal de un caso donde la ecuación sí aporta.

## Límites declarados
- D_hat es un proxy: la mitad de la varianza del área entre días, no una difusión estimada de incrementos. Para la prueba espectral habría que estimar D como en los bloques 8-9. Aquí solo fija la escala relativa de λ para comparar flujo y Bohm.
- 24 puntos por ciclo es poco; con datos reales se usa resolución de minutos.
- El modelo es un ejemplo con picos gaussianos. No reproduce fines de semana, clima ni tendencia; esos entran al pasar a datos reales, donde el chequeo de estacionariedad del bloque 9 cobra sentido.
- "Separable del ruido" aquí significa "distinguible de un nulo de desfase", no una descomposición formal.
