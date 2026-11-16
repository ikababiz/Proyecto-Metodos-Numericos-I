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

         [x_0,
   v_0 =  y_0,
          z_0]

3. Se introduce v_0 al sistema, obteniendo v_1, para después reintrodu-
   cirlo al sistema, obteniendo v_2. Y así sucesivamente, hasta que el
   vector incógnita converja.

Nota: El método no es exacto, así que deben tomarse los criterios de
      convergencia adecuados.
'''

import numpy as np

LOG = True

# Función que comprueba que la matriz es estrictamente diagonal dominante.
def diagonal_dominante(matriz):
    rows    = np.size(matriz, 0)
    columns = np.size(matriz, 1)

    '''
    Si la matriz no es cuadrada, no
    hay nada que se pueda hacer.
    '''
    if rows != columns:
        if LOG: print("No se trata de una matriz cuadrada.")
        return matriz, False

    valores_abs  = np.zeros(rows)
    matriz_copia = np.copy(matriz)

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
            matriz_copia[[i, aux_k]]   = matriz_copia[[aux_k, i]]
            matriz_copia[:,[i, aux_l]] = matriz_copia[:,[aux_l, i]]

            if LOG:
                print("-----------------------------")
                print("Iteración", i, ":\n", matriz_copia)
                print("-----------------------------")

            '''
            Actualizamos el valor sum_i^rows |a_ij|,
            con i != j, en el vector valores_abs.
            '''
            aux = abs(matriz_copia[i, i])
            valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - aux



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
            return matriz, False

    '''
    Si el proceso es exitoso, la matriz modificada es re-
    tornada junto con el valor booleano correspondiente.
    '''
    return matriz_copia, True


def generar_sistema(matriz):
    print("Lemus")


dominante = True
A = np.array([[9, 2, 0],
              [4, 0, 25],
              [5, 20, 0]])

print("La matriz A es:\n", A)

A, dominante  = diagonal_dominante(A)

print("La matriz final es:\n", A, "\nEs dominante:", dominante)
