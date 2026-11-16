# Bloque 1: pruebas con solución conocida

```bash
cd NucleoTG/analisis
pip install -r requirements.txt
python b1_validacion.py        # 1a + 1b + 1c (estimado: 3-6 min en un portátil)
python b1_validacion.py 1c     # solo una prueba
```

Salidas: tablas en pantalla y `resultados/b1a_rotacion.csv`, `b1b_ou.csv`, `b1c_fock_darwin.csv`.

`campos.py` es el núcleo común. Calcula P, ∇P, ∇²P, J y ∇J con derivadas analíticas del kernel, y u, ω, ∇·J y el término de Bohm a partir de ellos. La vorticidad también es analítica; el pipeline original usaba `np.gradient`.

## Cambio respecto al pipeline original: esquema de la corriente

El pipeline original calcula J con `K(r - r_k)·(r_{k+1} - r_k)/dt`, que es un esquema hacia adelante (tipo Itô). Ese esquema estima P·F (la deriva), **no** la corriente de probabilidad J = P·F − D∇P. El esquema de punto medio (`K(r - (r_k + r_{k+1})/2)·Δr/dt`, tipo Stratonovich) sí estima J. Para trayectorias deterministas suaves ambos convergen, pero difieren en la divergencia y en |u|², que es lo que entra en V. La prueba 1b lo discrimina.

Comprobación previa sin KDE, en Python puro, OU con γ = Ω = D = 1, dt = 0.01 y 4·10⁵ pasos. La regresión global de v sobre r dio:

| esquema | coef. radial | coef. azimutal | predicción |
|---|---|---|---|
| adelante | −1.018 | −0.996 | (−γ, −Ω) = (−1, −1) |
| medio | +0.000 | −1.001 | (0, −Ω) = (0, −1) |

## Predicciones declaradas ANTES de ejecutar

### 1a. Rotación rígida (N = 300 puntos gaussianos, σ = 1, una vuelta por periodo)

Referencia exacta, válida para cualquier conjunto finito de muestras con kernel gaussiano:

ω_ref = Ω_eff·(2 + h²·∇² ln P_B)

Aquí Ω_eff = 2 tan(Ω dt/2)/dt (medio) o sin(Ω dt)/dt (adelante). El valor ingenuo 2Ω **no** es la referencia correcta: el suavizado lo reduce. Para una nube gaussiana con N → ∞, ω ≈ 2Ω·σ²/(σ² + h²), es decir un factor 0.96, 0.89 y 0.80 para h = 0.2, 0.35 y 0.5.

| métrica | apoya el pipeline | lo refuta |
|---|---|---|
| `err_identidad` | ≲ 10⁻⁸ en ambos esquemas (comprueba el código de derivadas analíticas) | ≫ 10⁻⁶: error en `campos.py` |
| `div_rel`, adelante | ≈ O(Ω dt); baja como ~1/T | no baja con T |
| `div_rel`, medio | mucho menor que adelante y baja más rápido que 1/T | igual o mayor que adelante |
| `omega_med_2Om` | < 1, baja al subir h, del orden de σ²/(σ²+h²) (no exacto: N finito y promedio en la máscara) | ≈ 1 sin depender de h, o signo negativo |

### 1b. OU 2D, deriva −(γI + Ω𝒥)r, γ = Ω = D = 1, muestreo exacto, t_total = 5000, 3 semillas

Analítico: P = N(0, sI) con s = D/γ, velocidad de corriente −Ω𝒥r y rot = −2Ω. Con el suavizado, c_h = s/(s + h²). Las columnas ya están divididas por el valor esperado:

| métrica | medio | adelante | refuta |
|---|---|---|---|
| `radial` (÷ c_h·r) | ≈ 0 | ≈ −γ = −1 | medio claramente ≠ 0 |
| `azimutal` (÷ c_h·r) | ≈ −1 | ≈ −1 | lejos de −1 en ambos |
| `omega_rel` | ≈ 1 | ≈ 1 (la parte −γr no tiene rotacional) | ≠ 1 fuera del error entre semillas |
| `u2_rel` | ≈ 1 | ≈ (γ² + Ω²)/Ω² = 2 | medio ≈ 2 |
| `div_rel` | pequeña | grande (J_adelante = P·F no tiene divergencia nula) | medio ≈ adelante |
| `U_rmse_rel` | ≪ 1 (error estadístico del KDE) | igual (no depende del esquema) | ≳ 0.1 |

Consecuencia esperada para la línea 2: con el esquema hacia adelante, |u|² y por tanto V quedan sesgados por la componente de deriva. **Si 1b sale como se predice, el pipeline de Phasik debe pasar al esquema de punto medio.**

### 1c. Fock–Darwin (n = 0, l = 1, ω₀ = 1, ω_c = 2; ħ = m = q = 1; gauge simétrico)

E = 2Ω − ω_c/2 = 2√2 − 1 (verificado en Python puro en 4 puntos: V = ½ω₀²r² hasta 10⁻⁶). P y S se tratan como datos en la malla (caja [−4, 4]², diferencias finitas de 2.º orden); ∇S se obtiene de Im(z̄∇z) con z = e^{iS} para evitar el corte de rama.

| métrica | apoya | refuta |
|---|---|---|
| orden de convergencia sin ruido (`rmse_amplia`) | ≈ 2 (cociente ≈ 4 al dividir dx por 2) | < 1 o sin convergencia |
| `rmse_m5` frente a `rmse_amplia` | `rmse_m5` mayor: la máscara del 5 % llega hasta r ≈ 0.12, donde se cancelan dos términos ±1/(2r²) grandes; el error se concentra cerca del origen (`maxerr_r_lt_0p3`) | sin diferencia (no habría cancelación numérica) |
| forma P frente a √P | parecidas; la forma √P quizá algo peor cerca del origen (√P ∝ \|r\| tiene un pico cónico) | gran diferencia lejos del origen |
| con ruido ε | RMSE ≈ `pred_ruido` = ¼√20·ε/dx², creciente al **refinar** la malla | RMSE insensible a ε o a dx |

Si el último punto se cumple, demuestra que el problema inverso está mal condicionado: con datos ruidosos hace falta regularizar (suavizar P), y refinar la malla empeora el resultado. En la línea 2 ese papel lo cumple el ancho h del KDE.
