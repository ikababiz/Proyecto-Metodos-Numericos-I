#!/bin/python3

import numpy as np
import sympy as sp
import math

EPSILON = 0.0001

def f(x):
    return x**2 - x*math.exp(x) + 4

def xi(xc, xu, fc, fu):
    if abs(fu-fc) < EPSILON:
        return xu, False
    return xu - fu*(xu-xc)/(fu-fc), True

def print_values(i, x, fx):
    print("Iteración "+str(i)+" : x_"+str(i)+" =", f"{x:3.5f}", "f(x_"+str(i)+") =", f"{fx:3.5f}")

xc = 0
xu = 5
fc = f(xc)
fu = f(xu)
xaux, _ = xi(xc, xu, fc, fu)
faux = f(xaux)
print_values(1, xc, fc)
print_values(2, xu, fu)

i = 3
still = True
while still:
    print_values(i, xaux, faux)
    xc = xu
    fc = fu
    xu = xaux
    fu = faux
    xaux, still = xi(xc, xu, fc, fu)
    faux = f(xaux)
    i += 1
