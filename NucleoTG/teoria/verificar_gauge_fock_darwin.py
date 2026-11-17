"""
verificar_gauge_fock_darwin.py: comprobaciones del anteproyecto (solo biblioteca estándar).

    python verificar_gauge_fock_darwin.py

(A) Degeneración de la Ec. (9) en gauge de Coulomb, SIN simetría.
    Con A = grad_perp(Phi) = (d_y Phi, -d_x Phi), la continuidad div[P(grad S - qA)] = 0 se reduce a
        q {P, Phi} = div(P grad S),   {P, Phi} = d_x P d_y Phi - d_y P d_x Phi.
    Es una EDP de primer orden cuyas características son las curvas de nivel de P. Si Phi la cumple,
    Phi + F(P) también, para cualquier F: div(P grad_perp F(P)) = F'(P) {P, P} = 0.
    Pero B_z cambia en -lap F(P). La prueba usa una P elíptica y girada (sin simetría).

(B) Recuperación del potencial de confinamiento en estados de Fock-Darwin (n, l), incluidos excitados.
    hbar = m = q = 1, w0 = 1, wc = 2, gauge simétrico A = (B r / 2) theta_hat (que es de Coulomb).
    E_{n,l} = (2n + |l| + 1) Om - l wc / 2,  Om = sqrt(w0^2 + wc^2 / 4).
    P = R^2 con R = |psi|, S = l phi; se evalúa la Ec. (11) en puntos fuera de los nodos.
"""
import math

H = 1e-4
W0, WC = 1.0, 2.0
OM = math.sqrt(W0 ** 2 + WC ** 2 / 4)


def d(f, x, y, eje):
    if eje == 0:
        return (f(x + H, y) - f(x - H, y)) / (2 * H)
    return (f(x, y + H) - f(x, y - H)) / (2 * H)


def lap(f, x, y):
    return (f(x + H, y) + f(x - H, y) + f(x, y + H) + f(x, y - H) - 4 * f(x, y)) / H ** 2


def prueba_A():
    print("(A) Phi = F(P) en una P sin simetría: cumple la Ec. (9) y cambia B_z")
    P = lambda x, y: math.exp(-(x * x / 1.0 + y * y / 2.5 + 0.3 * x * y))   # noqa: E731
    F = lambda p: p ** 2 + math.sin(3 * p)                                    # noqa: E731
    Phi = lambda x, y: F(P(x, y))                                             # noqa: E731
    Ax = lambda x, y: d(Phi, x, y, 1)                                         # noqa: E731
    Ay = lambda x, y: -d(Phi, x, y, 0)                                        # noqa: E731
    for x, y in [(0.3, -0.7), (1.1, 0.4), (-0.8, 1.3)]:
        div = ((P(x + H, y) * Ax(x + H, y) - P(x - H, y) * Ax(x - H, y)) / (2 * H)
               + (P(x, y + H) * Ay(x, y + H) - P(x, y - H) * Ay(x, y - H)) / (2 * H))
        print(f"   ({x:+.1f},{y:+.1f})  div(P A) = {div:+.1e}   B_z añadido = {-lap(Phi, x, y):+.3f}")


def laguerre(n, a, x):
    if n == 0:
        return 1.0
    L0, L1 = 1.0, 1 + a - x
    for k in range(1, n):
        L0, L1 = L1, ((2 * k + 1 + a - x) * L1 - (k + a) * L0) / (k + 1)
    return L1


def prueba_B():
    print("(B) Ec. (11) en Fock-Darwin: |V_reconstruido - (1/2) w0^2 r^2| fuera de los nodos")
    for n, l in [(0, 0), (0, 1), (0, -1), (1, 0), (1, 1), (2, -2)]:
        E = (2 * n + abs(l) + 1) * OM - l * WC / 2

        def P(x, y, n=n, l=l):
            s = (x * x + y * y) * OM
            return (s ** (abs(l) / 2) * laguerre(n, abs(l), s) * math.exp(-s / 2)) ** 2
        err = 0.0
        for x, y in [(0.4, 0.3), (0.9, -0.6), (-1.3, 0.8), (0.2, 1.7)]:
            p = P(x, y)
            gx, gy = d(P, x, y, 0), d(P, x, y, 1)
            r2 = x * x + y * y
            ux = -l * y / r2 + WC * y / 2           # (grad S - qA)_x
            uy = l * x / r2 - WC * x / 2            # (grad S - qA)_y
            V = E - 0.5 * (ux * ux + uy * uy) + 0.25 * (lap(P, x, y) / p - 0.5 * (gx * gx + gy * gy) / p ** 2)
            err = max(err, abs(V - 0.5 * W0 ** 2 * r2))
        print(f"   (n,l) = ({n},{l:+d})  E = {E:.4f}  error máximo = {err:.1e}")


if __name__ == "__main__":
    prueba_A()
    prueba_B()
