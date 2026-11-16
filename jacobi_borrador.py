#!/bin/python3

''' Método de Jacobi
'''

import numpy as np

LOG = False

def diagonal_dominante(matriz):
    rows = np.size(matriz, 0)
    columns = np.size(matriz, 1)
    valores_abs = np.zeros(rows)
    matriz_copia = np.copy(matriz)

    for i in range(0, rows):
        aux = abs(matriz_copia.diagonal()[i])
        valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - aux

        if LOG: print("Valor de la suma de los absolutos:", valores_abs[i])

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
            https://stackoverflow.com/a/485798
            https://stackoverflow.com/a/54069951
            '''
            matriz_copia[[i, aux_k]] = matriz_copia[[aux_k, i]]
            matriz_copia[:,[i, aux_l]] = matriz_copia[:,[aux_l, i]]

            if LOG:
                print("-----------------------------")
                print("Iteración", i, ":\n", matriz_copia)
                print("-----------------------------")

            aux = abs(matriz_copia[i, i])
            valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - aux



    for i in range(0, rows):
        if valores_abs[i] >= abs(matriz_copia.diagonal()[i]):
            if LOG: print("No se trata de una matriz diagonal dominante.")
            return matriz, False

    matriz = np.copy(matriz_copia)
    return matriz_copia, True


def generar_sistema(matriz):
    print("Lemus")


dominante = True
A = np.array([[10, 2, 6],
              [4, 25, 4],
              [5, 0, 7]])

print("La matriz A es:\n", A)

A, dominante  = diagonal_dominante(A)

print("La matriz final es:\n", A, "\nEs dominante:", dominante)
