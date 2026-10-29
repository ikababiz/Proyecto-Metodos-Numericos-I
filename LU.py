#!/bin/python3

import numpy as np
from scipy.linalg import lu

A = np.array([[10, 2, 3], [4, 5, 6], [7, 8, 9]])
P, L, U = lu(A)

print(A)
print(P)
print(L)
print(U)
