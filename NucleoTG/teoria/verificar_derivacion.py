"""
verificar_derivacion.py: comprobación numérica de cada paso de derivacion_FP_Schrodinger.md.

Solo usa la biblioteca estándar (no necesita numpy):  python verificar_derivacion.py

Caso de prueba GENERAL (sin simetría): paisaje U no cuadrático y flujo estacionario construido
con una función de corriente, v = e^{U} Jm grad(Psi), que cumple div(e^{-U} v) = 0 por construcción.
Derivadas por diferencias centrales con paso 1e-3: los errores esperados son ~1e-5 (relativos).
"""
import cmath
import math

D = 0.7
H = 1e-3


def U(x, y):
    return 0.25 * (x * x + y * y) ** 2 + 0.3 * x - 0.2 * x * y


def Psi(x, y):
    return math.exp(-(x * x + y * y)) * (1 + 0.5 * y + 0.3 * x * x)


def grad(f, x, y):
    return ((f(x + H, y) - f(x - H, y)) / (2 * H), (f(x, y + H) - f(x, y - H)) / (2 * H))


def lap(f, x, y):
    return (f(x + H, y) + f(x - H, y) + f(x, y + H) + f(x, y - H) - 4 * f(x, y)) / H ** 2


def div(Fv, x, y):
    return ((Fv(x + H, y)[0] - Fv(x - H, y)[0]) / (2 * H)
            + (Fv(x, y + H)[1] - Fv(x, y - H)[1]) / (2 * H))


def v(x, y):
    gx, gy = grad(Psi, x, y)
    e = math.exp(U(x, y))
    return (-e * gy, e * gx)


def f(x, y):                       # deriva total f = -D grad U + v
    gx, gy = grad(U, x, y)
    vx, vy = v(x, y)
    return (-D * gx + vx, -D * gy + vy)


def Ps(x, y):
    return math.exp(-U(x, y))


def L(P, x, y):                    # operador de Fokker-Planck
    return -div(lambda a, b: (f(a, b)[0] * P(a, b), f(a, b)[1] * P(a, b)), x, y) + D * lap(P, x, y)


def Vs(x, y):                      # término de Bohm con lambda = 2D
    gx, gy = grad(U, x, y)
    return D * (0.25 * (gx * gx + gy * gy) - 0.5 * lap(U, x, y))


def H_sim(psi, x, y):              # H = -D lap + V_s + (1/2)(v.grad + div(v .))
    gx, gy = grad(psi, x, y)
    vx, vy = v(x, y)
    A = 0.5 * (vx * gx + vy * gy) + 0.5 * div(lambda a, b: (v(a, b)[0] * psi(a, b), v(a, b)[1] * psi(a, b)), x, y)
    return -D * lap(psi, x, y) + Vs(x, y) * psi(x, y) + A


def H_gauge(psi, x, y):            # H = D(-i grad - qA)^2 + V_FP,  qA = -i v/(2D),  V_FP = V_s + |v|^2/(4D)
    def qA(a, b):
        return (-1j * v(a, b)[0] / (2 * D), -1j * v(a, b)[1] / (2 * D))

    def Pi(a, b):
        return (-1j * (psi(a + H, b) - psi(a - H, b)) / (2 * H) - qA(a, b)[0] * psi(a, b),
                -1j * (psi(a, b + H) - psi(a, b - H)) / (2 * H) - qA(a, b)[1] * psi(a, b))
    dPi = (Pi(x + H, y)[0] - Pi(x - H, y)[0]) / (2 * H) + (Pi(x, y + H)[1] - Pi(x, y - H)[1]) / (2 * H)
    PiPi = -1j * dPi - (qA(x, y)[0] * Pi(x, y)[0] + qA(x, y)[1] * Pi(x, y)[1])
    vx, vy = v(x, y)
    return D * PiPi + (Vs(x, y) + (vx * vx + vy * vy) / (4 * D)) * psi(x, y)


def main():
    pts = [(0.3, -0.4), (-0.8, 0.5), (1.1, 0.9)]
    P = lambda x, y: math.exp(-0.5 * ((x - 0.2) ** 2 + 2 * (y + 0.1) ** 2)) * (1 + 0.4 * x * y)  # noqa: E731
    psi = lambda x, y: P(x, y) * math.exp(U(x, y) / 2)                                          # noqa: E731
    psi0 = lambda x, y: math.sqrt(Ps(x, y))                                                     # noqa: E731

    print("Paso 1. Estacionariedad: L P_s = 0 y div v = v . grad U")
    for x, y in pts:
        gx, gy = grad(U, x, y)
        vx, vy = v(x, y)
        print(f"  ({x:+.1f},{y:+.1f})  L P_s = {L(Ps, x, y):+.1e}   div v - v.gradU = {div(v, x, y) - (vx * gx + vy * gy):+.1e}")

    print("Paso 2-3. L P = -sqrt(P_s) H psi  (forma con V_s y término antihermítico)")
    for x, y in pts:
        print(f"  ({x:+.1f},{y:+.1f})  L P = {L(P, x, y):+.6f}   -sqrt(P_s) H psi = {-psi0(x, y) * H_sim(psi, x, y):+.6f}")

    print("Paso 4. sqrt(P_s) es el estado fundamental: H sqrt(P_s) = 0")
    for x, y in pts:
        print(f"  ({x:+.1f},{y:+.1f})  H sqrt(P_s) = {H_sim(psi0, x, y):+.1e}")

    print("Paso 5. Forma gauge: D(-i grad - qA)^2 + V_FP con qA = -i v/(2D) da la misma H")
    for x, y in pts:
        g = H_gauge(psi, x, y)
        print(f"  ({x:+.1f},{y:+.1f})  H_sim psi = {H_sim(psi, x, y):+.6f}   H_gauge psi = {g.real:+.6f} (imag {g.imag:+.0e})")

    print("Paso 6. V_FP en función de la deriva: V_s + |v|^2/(4D) = |f|^2/(4D) + (1/2) div f")
    for x, y in pts:
        vx, vy = v(x, y)
        fx, fy = f(x, y)
        a = Vs(x, y) + (vx * vx + vy * vy) / (4 * D)
        b = (fx * fx + fy * fy) / (4 * D) + 0.5 * div(f, x, y)
        print(f"  ({x:+.1f},{y:+.1f})  {a:+.6f}   {b:+.6f}")

    print("Paso 7. OU con rotación (gamma=1.3, Om=2): el término de flujo actúa como -Om d/dphi")
    g_, Om, m = 1.3, 2.0, 3
    for x, y in [(0.5, 0.2), (-0.4, 0.9)]:
        # para U = gamma r^2/(2D) y v = -Om Jm r:  A psi = v . grad psi  (div v = 0)
        ps = lambda a, b: (a * a + b * b) ** (m / 2) * cmath.exp(1j * m * math.atan2(b, a)) * math.exp(-(a * a + b * b))  # noqa: E731
        gx = (ps(x + H, y) - ps(x - H, y)) / (2 * H)
        gy = (ps(x, y + H) - ps(x, y - H)) / (2 * H)
        vx, vy = Om * y, -Om * x                     # -Om Jm (x, y) = -Om(-y, x)
        print(f"  ({x:+.1f},{y:+.1f})  (A psi)/psi = {(vx * gx + vy * gy) / ps(x, y):.5f}   esperado -i Om m = {-1j * Om * m}")
    print("  V_FP(OU) = (gamma^2 + Om^2) r^2/(4D) - gamma; espectro gamma (n1+n2) - i Om (n1-n2) (ver documento)")
    _ = g_


if __name__ == "__main__":
    main()
