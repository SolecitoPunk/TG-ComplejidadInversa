# Bloque 8b: seguimiento de la prueba de viabilidad

```bash
cd NucleoTG/analisis
python b8b_seguimiento.py     # estimado: 3-6 min
```

## Por qué existe
En el bloque 8, el control del código (A) falló por 0.009 en la frecuencia de OU (2.841 frente a un mínimo de 2.85). El umbral se mantiene. La prueba decisiva (B, Stuart–Landau) pasó con +21.7 % en la difusión de fase (límite 30 %), y el caso de pocos datos (C) con +29.7 %. Con una sola semilla y dos valores de h no se puede saber si esos márgenes son robustos.

## Criterios declarados ANTES de ejecutar
| prueba | condición | si falla |
|---|---|---|
| **1. Control con campos exactos** (OU y Stuart–Landau, sin datos) | \|err_re\| ≤ 0.02 y \|err_im\| ≤ 0.02 frente al FP verdadero | error de ensamblado de H (mío); se corrige antes de seguir. Si pasa, el fallo de A en el bloque 8 es sesgo de estimación y no del código |
| **2. Ley en h²** (todos los datos, medias de 5 semillas, 4 valores de h) | residuo del ajuste lineal re = a0 + c·h² ≤ 5 % de la media **y** a0 dentro del 10 % de la referencia | el sesgo no es una ley simple en h²; la extrapolación no es fiable y la viabilidad se limita a h pequeño |
| **3. Robustez en semillas** (h = 0.04, todos los datos) | `frac_ok` ≥ 0.8 (4 de 5 semillas) con \|re/ref − 1\| ≤ 0.30 y \|im/ref − 1\| ≤ 0.05 | los márgenes del bloque 8 eran suerte de la semilla |
| **4. Datos necesarios** | solo se reporta: ciclos frente a `frac_ok` (8400, 840, 250 y 84 ciclos) | sin umbral. Fija la cantidad mínima de ciclos que debe tener un conjunto de datos real para que valga la pena probarlo |

Expectativa, sin que cuente como prueba: 1 pasa. 2 es incierta (dos puntos del bloque 8 daban razón 3.9 frente a 4). 3 es incierta porque el margen del bloque 8 era del 8 %. En 4, espero que `frac_ok` baje con pocos ciclos y que h = 0.03 sea ruidoso con pocos datos.

## Límites
Todo en 2D, con D constante e isotrópica y sin memoria. Pasar estas pruebas no dice nada sobre anisotropía, estados no estacionarios ni proyecciones de datos reales. Tampoco responde si H reconstruido predice algo que no se obtenga más directamente de (P̂, v̂, D̂).
