import math

EPSILON = 1e-6  # valor muy pequeño > 0


def funcion(x): # la del ejemplo
    return x**2 - x * math.exp(x) + 4


def tabla(a, b, c, fa, fb, fc, n):
    print()
    print("_" * 59)
    print(f"|{n+1:<3d}|{a:<8.4f}|{b:<8.4f}|{c:<8.4f}|{fa:<8.4f}|{fb:<8.4f}|{fc:<8.4f}|", end="")


def main():
    # se elige a y b
    # Aquí se puede pedir al usuario que los ingrese y validar que f(a) tenga signo opuesto a f(b)
    a, b = -3.0, 2.0
    print("Método de la Falsa Posición")
    print("Con la ecuación x^2 - xe^x + 4 = 0")
    print("_" * 59)
    print(f"|{'n':<3}|{'a':<8}|{'b':<8}|{'c':<8}|{'f(a)':<8}|{'f(b)':<8}|{'f(c)':<8}|", end="")

    n = 0
    while abs(b - a) > EPSILON: # se puede tomar en consideración otros aspectos
        fa, fb = funcion(a), funcion(b)
        # se calcula c (antes de evaluar f(c))
        c = a - fa * (b - a) / (fb - fa)
        fc = funcion(c)
        tabla(a, b, c, fa, fb, fc, n)
        if abs(fc) < EPSILON:
            break
        if fa * fc > 0:
            a = c
        else:
            b = c
        n += 1
    print()


if __name__ == "__main__":
    main()
