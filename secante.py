import math

EPSILON = 1e-6  # valor muy pequeño > 0


def funcion(x): # la del ejemplo
    return x**2 - x * math.exp(x) + 4


def tabla(n, x_n, fx_n):
    print()
    print("_" * 23)
    print(f"|{n+1:<3d}|{x_n:<8.4f}|{fx_n:<8.4f}|", end="")


def main():
    n = 0
    print("Método de la Secante")
    print("Con la ecuación x^2 - xe^x + 4 = 0")
    print("_" * 23)
    print(f"|{'n':<3}|{'x_n':<8}|{'f(x_n)':<8}|", end="")

    x_n, x_n1 = 0.0, 3.0  # se eligen los primeros 2 o se piden
    fx_n = funcion(x_n)
    fx_n1 = funcion(x_n1)
    tabla(n, x_n, fx_n)
    tabla(n, x_n1, fx_n1)

    while abs(fx_n - fx_n1) > EPSILON:
        tempx = x_n  # para no perder el valor
        tempfx = funcion(tempx)
        x_n = x_n1  # se reasigna al cambiar de fila
        fx_n = funcion(x_n)
        x_n1 = x_n - fx_n * (x_n - tempx) / (fx_n - tempfx)
        fx_n1 = funcion(x_n1)
        tabla(n, x_n1, fx_n1)
        if abs(fx_n - fx_n1) < EPSILON:
            break
        n += 1
    print()


if __name__ == "__main__":
    main()
