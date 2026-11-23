# Resultados del bloque 1 (ejecutado por el autor; salida completa en los CSV de `resultados/`)

## 1a. Rotación rígida: predicciones cumplidas
- `err_identidad` ~ 1e-13 en todas las configuraciones: las derivadas analíticas de `campos.py` son correctas.
- `div_rel`, adelante: 0.0297, 0.0148, 0.0074, 0.0037 (h = 0.35; T = 51 a 408), exactamente ∝ 1/T.
- `div_rel`, medio: ~1e-16 desde T = 102; con T = 51 y h = 0.2 vale 1.8e-5 (aliasing). Decae mucho más rápido que 1/T.
- Media de ω/2Ω en la máscara = σ²/(σ²+h²) dentro del 0.3 %.
- **Hallazgo:** en el origen, ω/2Ω = 1.32 con h = 0.2 (el gaussiano daría 0.96), y la identidad ω = Ω(2 − h²∇²U) lo reproduce exactamente. Con N finito, una rotación uniforme da un mapa de vorticidad que copia la estructura de U. Por eso un mapa de ω estructurado no es evidencia por sí solo; hay que compararlo con la rotación rígida equivalente o con modelos nulos.

## 1b. OU: predicciones cumplidas
| dt = 0.01 (3 semillas) | adelante | medio | predicción |
|---|---|---|---|
| radial | −0.991 ± 0.006 | 0.001 ± 0.006 | −1 / 0 |
| azimutal | −0.982 ± 0.013 | −0.985 ± 0.016 | −1 |
| ω relativa | 0.971 ± 0.019 | 0.969 ± 0.015 | 1 |
| \|u\|² relativa | 1.95 ± 0.04 | 0.971 ± 0.032 | 2 / 1 |
| div_rel | 0.327 | 0.0026 | grande / pequeña |

Con dt = 0.05 hay un sesgo de ~5 % en la componente azimutal, que encaja con e^{−γdt} sin(Ωdt)/(Ωdt) = 0.951. **Decisión:** los bloques siguientes usan el esquema de punto medio.

## 1c. Fock–Darwin: una predicción refutada
- Orden de convergencia sin ruido ≈ 2 (P: 1.98, 2.19; √P: 1.64, 2.16). Sesgo pequeño: la E analítica es correcta.
- Ruido: el RMSE sigue `pred_ruido` = ¼√20·ε/dx² dentro del 2 % y crece al refinar la malla. Con ε = 1e-3 la mejor malla de las probadas es la de 129. El problema está mal condicionado y requiere regularización.
- **Refutada:** «las formas P y √P serán parecidas». √P es mejor en todas partes (malla de 65: `rmse_amplia` 0.051 frente a 1.009; error máximo cerca del origen 10 frente a 17). Explicación probable: P ∝ e^{−Ωr²} decae el doble de rápido que √P, y el error de diferencias finitas en las colas crece con ese exponente. Recomendación: usar la forma √P.
- El error puntual cerca del origen crece como 1/dx² (17 → 65 → 257). El RMSE converge solo porque la región afectada se encoge. Reportar la validación con esa salvedad.
