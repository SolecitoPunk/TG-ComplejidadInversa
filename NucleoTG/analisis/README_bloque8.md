# Bloque 8: prueba de viabilidad (sí o no) de la línea Fokker–Planck / Schrödinger

```bash
cd NucleoTG/analisis
python b8_espectro_sintetico.py     # estimado: 3-8 min
```

La teoría está en `../teoria/derivacion_FP_Schrodinger.md`.

## Qué compara

Para el primer modo oscilatorio λ = a + ib (a = tasa de relajación, b = frecuencia), cuatro fuentes:

1. **H reconstruido** a partir de (P̂, v̂, D̂), con λ = 2D̂ y signo + en el término de flujo. Es lo que se haría con datos reales.
2. **Autocorrelación** de z (OU) o de z/|z| (Stuart–Landau). Medición independiente de las mismas trayectorias, que no se usa para construir H.
3. **FP verdadero en la misma malla**, con la deriva exacta. Separa el error de estimación del error de discretización.
4. **Referencia analítica:** exacta en OU (γ ± iΩ = 1 ± 3i) y orientativa de ruido débil en Stuart–Landau (D_φ ≈ D(1+β²)/μ = 0.1, ω_eff ≈ ω − βμ = 5.28).

Además: D̂ frente a D, |λ₀| (debe ser ≈ 0), solape del estado fundamental con √P̂ (debe ser ≈ 1), dos anchos h, dos umbrales de máscara y dos tamaños de datos (todos y el 10 %).

## Criterios declarados ANTES de ejecutar

| puerta | condición | si falla |
|---|---|---|
| **A. OU (control del código)** | con todos los datos y al menos un h: \|a − 1\| ≤ 0.10, \|b − 3\| ≤ 0.15, \|λ₀\| < 0.05, solape > 0.98 | error de implementación; se corrige antes de concluir nada |
| **B. Stuart–Landau (viabilidad)** | con todos los datos y al menos un h, frente al FP verdadero: frecuencia dentro del 5 % y **tasa de difusión de fase dentro del 30 %**; además, la autocorrelación coincide con el FP verdadero en los mismos márgenes | **la línea no es viable**: si con datos ideales no se recupera la difusión de fase, con datos neuronales tampoco. Me quedo con la línea 1 |
| **C. Datos limitados** | B también con el 10 % de los datos (~800 ciclos) | viable solo con muchos datos; antes de seguir habría que comprobar que los datasets neuronales los tienen |

Lo que espero, sin que cuente como prueba: A pasa. En B, la frecuencia es fácil, pero la difusión de fase (a ≈ 0.1, unas 50 veces menor que la frecuencia) depende de la estructura radial fina del flujo, que el suavizado con h distorsiona. Es el punto débil y el que decide.

Si B pasa, la decisión no está tomada: los datos neuronales añaden anisotropía de D, memoria por la proyección a 2D y menos estacionariedad. B es necesaria, no suficiente.
