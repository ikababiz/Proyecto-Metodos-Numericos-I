import math

EPSILON = 1e-6  # valor muy pequeño > 0


def funcion(x): # la del ejemplo
    return x**2 - x * math.exp(x) + 4


def derivada(x): # calculada manualmente
    # 2x - e^x (x + 1)
    return 2 * x - math.exp(x) * (x + 1)


def tabla(n, xn, fxn, dfxn):
    print()
    print("_" * 32)
    print(f"|{n+1:<3d}|{xn:<8.4f}|{fxn:<8.4f}|{dfxn:<8.4f}|", end="")


def main():
    xn = 3.0  # se elige un punto cercano a la raíz, o se pide
    fxn = 1.0
    print("Método de Newton")
    print("Con la ecuación x^2 - xe^x + 4 = 0")
    print("_" * 32)
    print(f"|{'n':<3}|{'Xn':<8}|{'f(Xn)':<8}|{'f´(xn)':<8}|", end="")

    n = 0
    while abs(fxn) > EPSILON: # cuando sea casi cero
        fxn = funcion(xn)
        dfxn = derivada(xn)
        tabla(n, xn, fxn, dfxn)
        if abs(fxn) < EPSILON: 
            break
        xn = xn - fxn / dfxn
        n += 1
    print()


if __name__ == "__main__":
    main()
