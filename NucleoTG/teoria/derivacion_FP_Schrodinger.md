# De Fokker–Planck con corriente a la ecuación maestra extendida

Cada paso se comprueba numéricamente con `verificar_derivacion.py` (solo biblioteca estándar). Usa un paisaje U no cuadrático y un flujo estacionario general, sin ninguna simetría. Los errores relativos son de ~10⁻⁶, el nivel esperado con diferencias centrales de paso 10⁻³.

## 0. Qué es conocido y qué no

- **El caso sin corriente (balance detallado) es clásico:** el operador de Fokker–Planck es similar a un hamiltoniano de Schrödinger hermítico. Creo que está en Risken, *The Fokker–Planck Equation* (1989), cap. 5; hay que verificar la sección.
- **El caso con corriente también está publicado.** Mazzolo y Monthus, *Phys. Rev. E* 107, 014101 (2023), [arXiv:2210.05353](https://arxiv.org/abs/2210.05353), relacionan la dinámica de Fokker–Planck fuera del equilibrio con mecánica cuántica no hermítica: un potencial escalar real y un potencial vector puramente imaginario. Según el resumen, eligen el gauge según el propósito. **No pude leer el texto completo**, así que no sé si ya escriben la forma en el «gauge estacionario» de la sección 5. Hay que leerlo antes de afirmar cualquier novedad.
- **Lo que este documento añade, salvo que el artículo ya lo contenga:**
  1. Escribir la correspondencia en la forma del problema inverso: dados P_s, u y D, se recupera V.
  2. La comparación término a término con tu ecuación maestra, incluido el cambio de signo del término de flujo.
  3. La consecuencia operativa λ = 2D.

  Lo más probable es que el aporte del trabajo esté en la aplicación inversa a datos, no en la teoría.

## 1. Planteamiento y supuestos

Dinámica de Itô dr = f(r) dt + √(2D) dW, con **D constante e isotrópica** (supuesto fuerte; ver sección 9). La ecuación de Fokker–Planck es

∂ₜP = 𝓛P = −∇·(fP) + D∇²P = −∇·J,  J = fP − D∇P.

En el estado estacionario P_s = e^{−U} y J_s = P_s v. Aquí **v es la velocidad de corriente**, la misma cantidad u que se estima con el esquema de punto medio. El bloque 1b comprobó que el esquema hacia adelante no la estima.

## 2. Paso 1: descomposición de la deriva

De J_s = fP_s − D∇P_s = P_s(f + D∇U) se obtiene

**f = −D∇U + v.**

Estacionariedad: ∇·(P_s v) = 0. Como ∇·(e^{−U}v) = e^{−U}(∇·v − v·∇U), equivale a

**∇·v = v·∇U.**  (verificado, paso 1)

## 3. Paso 2: transformación de similaridad, parte de gradiente

Se escribe P = e^{−U/2}ψ = √P_s ψ. La parte de gradiente es 𝓛_g P = D∇·(∇P + P∇U).

- ∇P = e^{−U/2}(∇ψ − ½ψ∇U)
- ∇P + P∇U = e^{−U/2}(∇ψ + ½ψ∇U)
- ∇·(…) = e^{−U/2}[∇²ψ + ½∇U·∇ψ + ½ψ∇²U − ½∇U·∇ψ − ¼ψ|∇U|²]

Resultado:

𝓛_g P = −√P_s [−D∇² + V_s] ψ,  **V_s = D(¼|∇U|² − ½∇²U).**

## 4. Paso 3: parte de corriente

−∇·(vP) = −e^{−U/2}[(∇·v)ψ + v·∇ψ − ½(v·∇U)ψ].

Con el paso 1, ∇·v − ½v·∇U = ½∇·v, así que

−∇·(vP) = −√P_s 𝒜ψ,  **𝒜 = ½(v·∇ + ∇·(v ·)).**

𝒜 es **antihermítico**: (v·∇)† = −v·∇ − (∇·v), luego 𝒜† = −𝒜.

## 5. Resultado: hamiltoniano no hermítico (verificado, pasos 2-3)

∂ₜψ = −Ĥψ,  **Ĥ = −D∇² + V_s + 𝒜**

La parte −D∇² + V_s es hermítica y la parte 𝒜 es antihermítica. Si v = 0, se recupera el caso clásico de balance detallado.

**Estado fundamental (paso 4):** como 𝓛P_s = 0, se cumple Ĥ√P_s = 0. El autovalor 0 corresponde a la función √P_s, igual que en el ansatz ψ = √P e^{iS} de tu línea 1.

## 6. Paso 5: forma con potencial vector (gauge estacionario)

Con la identificación ħ = 1 y ħ²/2m = D (es decir, m = 1/(2D)):

**Ĥ = D(−i∇ − qA)² + V_FP,  qA = −i v/(2D),  V_FP = V_s + |v|²/(4D).**  (verificado, paso 5)

El potencial vector es **imaginario** y proporcional a la velocidad de corriente. Al desarrollar el cuadrado aparece −|v|²/(4D), y V_FP lo compensa con +|v|²/(4D).

## 7. Paso 6: invariancia de gauge

Un cambio de gauge imaginario ψ → e^{χ}ψ es una transformación de similaridad: no cambia el espectro y desplaza qA por un gradiente. Dos consecuencias:

- **V_FP es invariante.** En el gauge de la deriva completa vale V_FP = |f|²/(4D) + ½∇·f, que es la forma habitual en la literatura. En el gauge estacionario vale V_s + |v|²/(4D). Son el mismo campo (verificado, paso 6).
- **El campo magnético imaginario es invariante:** ∇×(qA) ∝ ∇×v = ∇×f, porque f y v difieren en un gradiente. La vorticidad de la velocidad de corriente medida es el rotacional de la deriva, la firma estándar de una fuerza no conservativa. Es el análogo exacto de tu afirmación de la línea 1 de que lo interpretable es ∇×u = −qB.

## 8. Comparación con la ecuación maestra extendida (línea 1)

| | cuántico (línea 1) | Fokker–Planck estacionario |
|---|---|---|
| amplitud | √P | √P_s |
| velocidad | u = (∇S − qA)/m, real | v = J_s/P_s, real |
| potencial vector | real | **imaginario**, qA = −iv/(2D) |
| constante λ = ħ²/m | libre en redes | **λ = 2D** (fijada por el ruido) |
| término de Bohm | (λ/4)[∇²P/P − ½\|∇P\|²/P²] | igual, con λ = 2D (V_s) |
| término de flujo | **−½m\|u\|²** | **+½m\|v\|²** = \|v\|²/(4D) |
| energía | E | 0 (estado fundamental) |
| invariante de gauge | ∇×u ∝ B | ∇×v = ∇×f |

En fórmula, la versión de Fokker–Planck de tu ecuación maestra es

**V_FP = (D/2)[∇²P_s/P_s − ½|∇P_s|²/P_s²] + |v|²/(4D).**

**Consecuencia para la línea 2:** usar la ecuación maestra cuántica (signo −) en datos con ruido no es la analogía correcta. Si se quiere que V tenga significado dinámico, hay que usar el signo + y λ = 2D. Esto no es un ajuste: es lo que sale de la derivación. En los bloques 3 y 6 usé el signo − con λ libre, así que **esos resultados sobre V no aplican a V_FP**. Los resultados sobre U, u, vorticidad y circulación sí siguen valiendo.

## 9. Ejemplo exacto: OU con rotación

Con f = −(γI + Ω𝒥)r:

- U = γr²/(2D) y v = −Ω𝒥r, con ∇·v = 0.
- V_s = γ²r²/(4D) − γ: un oscilador armónico 2D de frecuencia γ.
- 𝒜 = v·∇ = −Ω∂_φ. Sobre e^{imφ} vale −iΩm (verificado, paso 7).
- 𝒜 conmuta con la parte hermítica por la simetría rotacional, así que el espectro es

**λ_{n₁,n₂} = γ(n₁ + n₂) − iΩ(n₁ − n₂).**

Coincide con el espectro conocido del OU con rotación. **Las partes reales (relajación) vienen del término de Bohm; las imaginarias (oscilación), del flujo.**

En este ejemplo V_FP = (γ² + Ω²)r²/(4D) − γ es más rígido que V_s. El término A² del potencial vector imaginario compensa exactamente ese exceso, de modo que el espectro real no depende de Ω.

## 10. Qué se puede poner a prueba con datos

Todo lo anterior se calcula a partir de (P_s, v, D). **Sigue sin haber información nueva**: con (P_s, v, D) se puede reconstruir f = −D∇U + v y estudiar Fokker–Planck directamente. Lo que sí ofrece esta formulación es una **prueba de consistencia falsable** y una lectura en el lenguaje de la línea 1:

1. Con trayectorias se estiman P̂_s (KDE), v̂ (punto medio) y D̂ (varianza de los incrementos).
2. Se construye Ĥ en una malla y se calculan sus primeros autovalores no nulos λ₁ = a + ib.
3. **Predicción:** la autocorrelación de observables, por ejemplo e^{iθ(t)} en un ciclo, debe decaer con tasa a y oscilar con frecuencia b. Esto se mide de forma independiente en las series y no se usa en la construcción de Ĥ.
4. Si coincide, el modelo de difusión estacionaria con D constante describe los datos, y V_FP y ∇×v son descripciones válidas del paisaje y de la parte no conservativa. Si no coincide, alguno de los supuestos falla (estacionariedad, D constante, markovianidad en el plano elegido), y eso es informativo.

## 11. Supuestos y riesgos

- **D constante e isotrópica.** En datos reales, sobre todo en planos de PCA neuronales, D será anisotrópica y dependerá del estado. Con D(r) aparece la ambigüedad de Itô o Stratonovich y la transformación se complica. Habría que estimar el tensor D y, como mínimo, comprobar cuánto se aleja de la isotropía.
- **Estacionariedad.** Hacen falta muchos ciclos de un régimen estacionario. **Las rotaciones neuronales de las tareas de alcance (Churchland et al. 2012) son transitorias:** cada ensayo empieza en otro punto y dura un movimiento. Ahí P_s no existe y la continuidad estacionaria no se cumple. Son mejores las tareas rítmicas, con oscilación sostenida durante muchos ciclos. Creo que hay datos de corteza motora en una tarea de pedaleo con el brazo (Russo et al. 2018), pero hay que confirmar si son públicos.
- **Markovianidad en 2D.** Proyectar una dinámica de alta dimensión a un plano introduce memoria. Es probablemente la causa más seria de que la prueba del punto 10 falle con datos reales.
- **Debate sobre las rotaciones.** [Lebedev et al. 2019](https://www.nature.com/articles/s41598-019-54760-4) argumentan que las rotaciones aparecen cuando los picos de las neuronas siguen una secuencia consistente, y [un trabajo de 2024](https://www.nature.com/articles/s41598-024-53907-2) las atribuye a ondas viajeras. Los modelos nulos del bloque 5 son justo lo que hace falta para responder a esa crítica.

## 12. Siguiente paso técnico

Benchmark sintético antes de cualquier dato real:

1. OU con rotación: espectro exacto conocido (sección 9).
2. Oscilador de Stuart–Landau con ruido: ciclo límite. El primer autovalor no nulo da la difusión de fase y la frecuencia, y se pueden contrastar con la autocorrelación.

En ambos se estiman (P̂, v̂, D̂) a partir de trayectorias simuladas y se mide si el espectro de Ĥ predice la autocorrelación.
