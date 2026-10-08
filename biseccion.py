import math

EPSILON = 1e-6  # valor muy pequeño > 0


def funcion(x): # la del ejemplo
    return x**2 - x * math.exp(x) + 4 


def tabla(a, b, c, fa, fb, fc, n):
    print()
    print("_" * 59)
    print(f"|{n+1:<3d}|{a:<8.4f}|{b:<8.4f}|{c:<8.4f}|{fa:<8.4f}|{fb:<8.4f}|{fc:<8.4f}|", end="")

def leer_numero(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Error, ingrese un número válido.")

def main():
    print("Método de Bisección")
    print("Con la ecuación x^2 - xe^x + 4 = 0")
    while True:
        a = leer_numero("Ingrese el valor de a: ")
        b = leer_numero("Ingrese el valor de b: ")
        fa, fb = funcion(a), funcion(b)

        if a >= b:
            print("Error, a debe ser menor que b.")
        elif fa * fb >= 0:
            print(f"Error, los signos de f({a}) y f({b}) deben ser distintos.")
        else:
            break

    print("_" * 59)
    print(f"|{'n':<3}|{'a':<8}|{'b':<8}|{'c':<8}|{'f(a)':<8}|{'f(b)':<8}|{'f(c)':<8}|", end="")

    n = 0
    while abs(b - a) > EPSILON: # se puede tomar en consideración otros aspectos
        c = (a + b) / 2
        fa, fb, fc = funcion(a), funcion(b), funcion(c)
        tabla(a, b, c, fa, fb, fc, n)
        if abs(fc) < EPSILON: # cuando f(c) es casi cero
            break
        if fa * fc > 0: 
            a = c
        else:
            b = c
        n += 1
    print()
    print("_" * 59)
    print(f"La raiz aproximada de x^2 - xe^x + 4 = 0 es: {c:<4.5}")
    print('Fin del programa')


if __name__ == "__main__":
    main()
