# Recomendación de modalidad

**Recomendación: Monografía de investigación teórica** (Acuerdo 004 de 2026, Art. 2 lit. b; anteproyecto según Art. 24; informe final según Art. 25; evaluación según Art. 26).

Alcance: solo el caso cuántico. Problema inverso con potencial vector, unicidad y fijación de gauge, validación en Fock–Darwin y lectura desde Barad y Latour. Las aplicaciones a sistemas no cuánticos quedan fuera. La correspondencia con Fokker–Planck queda como perspectiva.

## Comparación (verificada contra el texto completo del Acuerdo 004 de 2026)

| criterio | Monografía teórica | Artículo académico | Investigación / Creación / Innovación | Pasantía de investigación |
|---|---|---|---|---|
| Base | Art. 2 b; Arts. 24–26 | Art. 2 d; Arts. 31–34 | Art. 2 a; Arts. 20–23 | Art. 2 f; Arts. 38–44 |
| Requisito clave | 70 % de créditos; aval del director; Comité de Bioética e Investigación y Consejo Curricular | Estudiantes como primeros autores; aceptación en revista indexada; filiación UD (Art. 33 par. 4) | Vínculo a grupo, semillero, instituto o centro UD, o reconocido por Minciencias con ≥ 1 año; convocatoria y cupos (Art. 20) | ≥ 384 h; entidad legal o unidad UD; carta y profesional responsable; ARL antes de iniciar |
| Evaluación | Jurado: escrito 60 % y sustentación 40 % (Art. 26) | Ordinario: nota del director, con socialización obligatoria sin nota. Excepcional: un jurado (Art. 33 par. 5) | Promedio del director y del jurado (Art. 23) | Concepto del profesional externo y socialización evaluada por el director interno y el externo (Art. 44 par. 2) |
| Distinción meritoria | Aporta nuevos conocimientos (Art. 60 a) | Publindex B o WoS/Scopus Q3 | Nuevos conocimientos o apropiación social | Aportes excepcionales |
| Distinción laureada | Contribuye a definir nuevas fronteras | Publindex A1–A2 o Q1–Q2 | Aporte evidente a un producto de PI de un grupo institucionalizado | Impacto significativo y demostrable |
| Encaje con este trabajo | **alto** | medio: la parte filosófica no cabe en una revista de física, y depende de plazos editoriales | medio: solo si ya hay semillero o grupo | bajo: no hay estancia que lo requiera |

Comunes a todas: un docente director de carrera o TCO/MTO (Art. 10); el director no es autor (Art. 10 par. 2 y Art. 31); una sola modalidad a la vez, con un único cambio (Art. 13); nota mínima de 4.5 para meritoria y 5.0 para laureada (Art. 59), evaluada por dos jurados expertos (Art. 60 par. 2).

## Por qué Monografía
1. Es la única modalidad que acoge completos los tres componentes del trabajo: la derivación y el problema de unicidad, el código validado y el marco de Barad y Latour.
2. No depende de convocatorias de semillero (Art. 20), de plazos editoriales (Art. 9 y Art. 33 par. 5) ni de trámites de ARL.
3. Tras la sustentación, el núcleo físico-computacional puede someterse como artículo independiente.

## Correcciones al informe de modalidad recibido
- **El Acuerdo sí está completo.** El PDF adjunto tiene las 36 páginas, sin saltos entre los artículos 3–31 y 38–59. La propiedad intelectual sí tiene articulado propio: Art. 14 y Art. 62, que remiten al Acuerdo 04 de 2012 del CSU.
- **Duración (Art. 9):** un periodo si el plan tiene un espacio de Trabajo de Grado y dos si tiene dos. Hay una prórroga del Consejo Curricular y, excepcionalmente, otra del Consejo de Facultad. «Dos semestres» depende del plan de Física; confirmarlo con la coordinación.
- **Pasantía:** el Acuerdo no fija el 50 % / 50 %. Remite a los porcentajes del formato del programa (Art. 44 par. 2).
- **Monografía:** la radicación requiere también el aval del Comité de Bioética e Investigación (Art. 24).
- Las afirmaciones sobre el Acuerdo 04 de 2012 del CSU (titularidad del software y derechos patrimoniales) no las pude verificar. Hay que contrastarlas con el estatuto.

## Correcciones técnicas incorporadas al anteproyecto
- **El gauge de Coulomb no cierra el sistema en 2D.** En `q{P, Φ} = ∇·(P∇S)`, si Φ es solución, Φ + F(P) también lo es para cualquier F, y B_z cambia. Se verificó con una densidad elíptica sin simetría (`verificar_gauge_fock_darwin.py`, prueba A): la divergencia queda en ~10⁻⁹ y B_z cambia en 0.2–2.2. La degeneración axial es el caso particular F(P(r)). La unicidad exige prescribir B_z o V.
- **«Verificado simbólicamente» se sustituye por la comprobación real:** recuperación numérica puntual del confinamiento para (n, l) = (0,0), (0,±1), (1,0), (1,1) y (2,−2), fuera de los nodos, con error ≤ 3·10⁻⁶ (prueba B). La verificación simbólica y la versión en malla quedan como trabajo.
- **Nodos radiales (n > 0):** ψ cambia de signo, así que con R = |ψ| la fase salta en πħ. La recuperación vale fuera del conjunto nodal.
- **Lo que no he podido confirmar.** La afirmación de que Bhalgamiya y Novotny «advierten» que su método no sirve con campo magnético necesita el texto completo del artículo. Queda como nota al pie en el anteproyecto.

## Pendiente antes de radicar
- **`extended_inverse_solver` no está en el repositorio.** El código validado que existe es `NucleoTG/analisis/b1_validacion.py` (función `fock_darwin`) junto con `campos.py`. Si ese solver existe en otro lugar, hay que subirlo; si no, el anteproyecto ya lo describe como «resolvedor por implementar».
- Rellenar nombre, director y programa; compilar el `.tex`; verificar la bibliografía.
