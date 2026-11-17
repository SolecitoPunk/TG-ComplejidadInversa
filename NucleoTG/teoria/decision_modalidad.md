# Alcance y modalidad del trabajo de grado, en resumen

## Alcance decidido
**Dentro:**
1. Problema inverso de Schrödinger con potencial vector (generalización de Bhalgamiya y Novotny), validado en Fock–Darwin.
2. Desarrollo analítico de la correspondencia con Fokker–Planck con corriente: operador no hermítico, λ = ħ²/m = 2D, potencial vector imaginario, cambio de signo del término de flujo, invariancia de gauge.
3. Caso puente nuevo: el OU con rotación es Fock–Darwin con ω_c = 2iΩ (verificado en los autovalores; `derivacion_FP_Schrodinger.md`, sección 9b).
4. Batería de pruebas numéricas con solución conocida (P1–P8) y criterios declarados antes de ejecutar.
5. Marco filosófico: Barad (realismo agencial) y Latour (actor-red, referencia circulante).

**Fuera (trabajo futuro):** aplicación de la ecuación a sistemas no físicos (red de levadura, bicicletas, datos neuronales).

## Por qué se dejó fuera la aplicación a sistemas no físicos
- **Red de levadura (Phasik):** la extensión con flujo no aportó información medible frente a la línea base; la única señal no sobrevivió a un nulo por nodos.
- **Bicicletas y ciclos sociales:** son osciladores forzados por el reloj; la correspondencia supone dinámica estacionaria autónoma.
- **Datos neuronales públicos revisados:** grabación secuencial y promediada, sin la difusión que el método necesita.

Esos resultados se conservan en el repositorio (bloques 1–7 y 10) como antecedente del recorte. La parte analítica y las pruebas sintéticas (bloques 8–9b y la teoría) son sólidas y bastan para un trabajo de grado.

## Modalidad recomendada
**Monografía de investigación teórica** (Acuerdo 004 de 2026, cap. V, Art. 24–26). Con el nuevo alcance encaja todavía mejor: el aporte es analítico, numérico y epistemológico, sin componente empírico central.

| modalidad | encaje |
|---|---|
| **Monografía teórica** | la más adecuada; no exige vínculo a semillero |
| Investigación / Investigación-Creación | viable si hay semillero institucionalizado (Art. 20); da acceso a distinción laureada |
| Artículo académico | mejor como producto derivado: depende de la aceptación de una revista dentro del plazo del Art. 9 |

## Cómo trabaja la filosofía en este alcance
- **Barad**, en el nivel ontológico-epistemológico:
  - el gauge como especificación del aparato; lo que se conserva entre gauges (rotacional, espectro) es lo reproducible a través de cortes;
  - el ancho de suavizado h como parte del fenómeno medido (ley h²);
  - un campo magnético real y uno imaginario comparten la forma matemática, pero materializan prácticas distintas.
- **Latour**, en el nivel de la práctica: la cadena ecuación → código → tabla → afirmación, con mediadores no humanos (esquema de corriente, estimador de D, script de verificación). Fundamenta declarar criterios antes de ejecutar y registrar correcciones.
- Se mantiene la distinción que la propia Barad hace entre su aparato y la red de Latour.

## Archivos
- `propuesta_trabajo_grado.tex`: propuesta formal (estructura del Art. 24).
- `informe_director.tex`: informe para el director con el estado y las preguntas pendientes.
- `derivacion_FP_Schrodinger.md` y `verificar_derivacion.py`: derivación y verificación numérica (pasos 1–8).

## Antes de radicar
- Rellenar nombre, director y programa.
- Compilar (Overleaf o `pdflatex`); el PDF no se generó en el sandbox.
- Verificar los datos bibliográficos contra las fuentes, en especial Mazzolo y Monthus, Fock (1928) y Darwin (1931).
- Confirmar con la coordinación si el programa exige una plantilla propia (Art. 4a).
