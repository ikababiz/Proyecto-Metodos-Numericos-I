#!/bin/python3

''' Método de Jacobi

El método de Jacobi es un método numérico para encontrar las incógnitas
de un sistema de ecuaciones lineales de forma aproximada a través de i-
teraciones.

Requisitos:

- Que la matriz de coeficientes del sistema sea cuadrada.
- Que la matriz de coeficientes del sistema sea diagonal estrictamente
  dominante.

Una vez que el sistema cumple con los requisitos, se procede con el al-
goritmo:

1. Dado el sistema, se despeja cada ecuación respecto a la variable de
   la diagonal correspondiente. De aquí se intuye el algoritmo itera-
   tivo:

   a_1x + b_1y + c_1z = r_1      x_{n+1} = (r_1 - b_1y_n - c_1z_n)/a_1
   a_2x + b_2y + c_2z = r_2  ->  y_{n+1} = (r_2 - a_2x_n - c_2z_n)/b_2
   a_3x + b_3y + c_3z = r_3      z_{n+1} = (r_3 - a_3x_n - b_3y_n)/c_3

2. Se propone un vector solución inicial (puede ser cualquiera).
         
   v_0 = (x_0, y_0, z_0)

3. Se introduce v_0 al sistema, obteniendo v_1, para después reintrodu-
   cirlo al sistema, obteniendo v_2. Y así sucesivamente, hasta que el
   vector incógnita converja.

Nota: El método no es exacto, así que deben tomarse los criterios de
      convergencia adecuados.
'''

import numpy as np
import sympy as sp

LOG = True
MAX_ITER = 100
MIN_DIFF = 0.0000001

def print_iteracion(i, diagonal, rows):
    print("Iteración "+str(i)+":")
    for j in range(rows):
        print("\tx_"+str(j)+": "+f"{diagonal['x_'+str(j)]:3.5f}")

# Función que verifica que la matriz es diagonal estrictamente dominante.
def diagonal_dominante(matriz, vector):
    rows    = np.size(matriz, 0)
    columns = np.size(matriz, 1)

    if rows != columns: # Si la matriz no es cuadrada, no hay nada que se pueda hacer.
        if LOG: print("No se trata de una matriz cuadrada.")
        return matriz, vector, False

    valores_abs  = np.zeros(rows)
    matriz_copia = np.copy(matriz)
    vector_copia = np.copy(vector)
    vector_permutado = np.arange(rows)
    vector_permutado_copia = np.copy(vector_permutado)
    vector_permutado_x = np.copy(vector_permutado)
    vector_permutado_x_copia = np.copy(vector_permutado_x)
    matriz_permutada = np.identity(rows)
    matriz_permutada_copia = np.copy(matriz_permutada)

    for i in range(0, rows):
        '''
        El vector valores_abs contendrá sum_j^{rows} |a_ij|,
        con i != j, en cada entrada correspondiente i.
        '''
        aux = abs(matriz_copia.diagonal()[i])
        valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - aux

        if LOG: print("Valor de la suma de los absolutos:", valores_abs[i])

        '''
        Si |a_ii| <= sum_j^rows |a_ij|, con i != j, entonces bus-
        camos en la submatriz subyacente a max{|a_ij|} y guarda-
        mos su posición en las variables aux_k y aux_l.
        '''
        if aux <= valores_abs[i]:
            aux_k, aux_l = i, i
            for k in range(i, rows):
                for l in range(i, columns):
                    aux_dos = abs(matriz_copia[k, l])
                    if aux < aux_dos:
                        aux = aux_dos
                        aux_k, aux_l = k, l

            if LOG: print("[ k =", aux_k, ", l =", aux_l,"]")

            '''
            Una vez se tiene la posición de max{|a_ij|}, manipulamos
            la matriz tal que este valor tome la posición de a_ii.
            '''
            matriz_copia[:,[i, aux_l]] = matriz_copia[:,[aux_l, i]]
            matriz_copia[[i, aux_k]]   = matriz_copia[[aux_k, i]]

            matriz_permutada_copia[:,[i, aux_l]] = matriz_permutada_copia[:,[aux_l, i]]
            matriz_permutada_copia[[i, aux_k]]   = matriz_permutada_copia[[aux_k, i]]

            vector_copia[i], vector_copia[aux_k] = vector_copia[aux_k], vector_copia[i]

            vector_permutado_copia[i], vector_permutado_copia[aux_k] = vector_permutado_copia[aux_k], vector_permutado_copia[i]
            vector_permutado_x_copia[i], vector_permutado_x_copia[aux_l] = vector_permutado_x_copia[aux_l], vector_permutado_x_copia[i]

            if LOG:
                print("-----------------------------")
                print("Iteración", i, ":\n", matriz_copia)
                print("-----------------------------")

            # Actualizamos el valor sum_i^rows |a_ij|, con i != j, en el vector valores_abs.
            valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - abs(matriz_copia.diagonal()[i])



    '''
    Una vez acaba el proceso de pivoteo, verificamos si este
    resultó en una matriz diagonal estrictamente dominante.
    De no serlo, significa que la matriz no posee tal carac-
    terística, y se retorna la matriz original junto con un
    valor booleano que indica la ausecia de dicha propiedad.
    '''
    for i in range(0, rows):
        if valores_abs[i] >= abs(matriz_copia.diagonal()[i]):
            if LOG: print("No se trata de una matriz diagonal dominante.")
            return matriz, vector, matriz_permutada, vector_permutado, vector_permutado_x, False

    '''
    Si el proceso es exitoso, la matriz modificada es re-
    tornada junto con el valor booleano correspondiente.
    '''
    return matriz_copia, vector_copia, matriz_permutada_copia, vector_permutado_copia, vector_permutado_x_copia, True


dominante = True
A = np.array([[9, -2, 0],
              [4, 2, -25],
              [-2, -20, 1]])
b = np.array([-3, 2, 1])

rows = np.size(A, 0)
columns = np.size(A, 1)

print("La matriz A es:\n", A, "\nEl vector solución es:\n", b)

# Comprobación con SymPy.
Asp = sp.Matrix(A)
bsp = sp.Matrix(b)
x = Asp.LUsolve(bsp)

print("Resultado según SymPy:")
resultado_sympy = sp.N(x)
for j in range(rows):
    print("\tx_"+str(j)+": "+f"{resultado_sympy[j]:3.5f}")

A, b, P, pb, px, dominante = diagonal_dominante(A, b)

print("La matriz final es:\n", A, "\nEl vector solución final es:\n", b, "\nEs dominante:", dominante, "\nSu matriz de permutación es:\n", P, "\nSu vector solución permutado es:\n", pb, "\nSu vector incógnita permutado es:\n", px)

if not dominante: exit(1)

diagonal = {}
vector_n = np.array([1, 2, 3])
ecuaciones = [""] * rows
despejados = [None] * rows

for i in range(rows):
    ecuaciones[i] += "("+str(b[i])
    for j in range(columns):
        if i != j: ecuaciones[i] += " - "+str(A[i, j])+"*x_"+str(px[j])
    ecuaciones[i] += ")/"+str(A[i, i])
    despejados[i] = sp.parse_expr(ecuaciones[i])
    diagonal["x_"+str(i)] = vector_n[i]

if LOG: print("Ecuaciones:", ecuaciones, "\nDespejados:", despejados, "\nVariables:", diagonal)

vector_n1 = np.zeros(rows)
vector_diff = np.zeros(rows)
parar = [False] * rows

i = 0
vector_n = vector_n[px]
while i < MAX_ITER and not all(parar):
    for j in range(rows):
        vector_n1[j] = despejados[j].evalf(subs=diagonal)
        vector_diff[j] = abs(vector_n1[j] - vector_n[j])
        parar[j] = MIN_DIFF > vector_diff[j]

    vector_n = np.copy(vector_n1)
    '''
    Nos basamos en px[j] porque son las ecuaciones evaluadas las que
    no siguen el orden del vector, pues pueden cambiar según se cam-
    biaron columnas en la matriz A. Si no se hicieron cambios en las
    columnas, px[j] = j.
    '''
    diagonal = {"x_"+str(px[j]): vector_n1[j] for j in range(rows)}

    print_iteracion(i, diagonal, rows)

    if LOG:
        print("----------------------")
        for j in range(rows):
            print("x_"+str(j)+" convergió: "+str(parar[j]))
        print("----------------------")
    i += 1

if i == MAX_ITER and not all(parar): print("Se agotaron las iteraciones.")

print("Solución al sistema:")
for j in range(rows):
    print("\tx_"+str(j)+": "+f"{diagonal['x_'+str(j)]:3.5f}")
