#!/bin/python3

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import math

def f(x):
    return x**2 - x*np.exp(x) + 4

def nueva_c(a, b, fa, fb):
    return a - (fa*(b-a))/(fb - fa) # Punto (c, 0) para una recta.

# Rango inicial [a, b].
a = -3
b =  3

fa = f(a)
fb = f(b)

c = nueva_c(a, b, fa, fb)
fc = f(c)
c_values = np.array([c])   # Arreglo con los valores de c_n.
fc_values = np.array([fc]) # Arreglo con los valores de f(c_n).

x = np.linspace(a, b)      # Dominio de la gráfica.
y = x**2 - x*np.exp(x) + 4 # Expresión a dibujar en la gráfica.

epsilon = 0.001 # Diferencia mínima.

a_fijo = True
b_fijo = True

i = 1
print("Iteración", i, ": a =", f"{a:3.5f}", "b =", f"{b:3.5f}", "c =", f"{c:3.5f}", "f(a) =", f"{fa:3.5f}", "f(b) =", f"{fb:3.5f}", "f(c) =", f"{fc:3.5f}")
if np.sign(fa) == np.sign(fb): # Si f(a) y f(b) son del mismo signo, aborta el programa.
    print("La solución no es posible en el rango dado\n")
    exit(1)
while abs(fc) > epsilon: # Iterar hasta que la distancia entre f(c) y la recta x sea menor a epsilon.
    i += 1 # Seguir la iteración.
    if np.sign(fa) == np.sign(fc): # Si f(a) y f(c) son del mismo signo,
        fa = fc                    # reemplazamos f(a) con f(c) y también
        a = c                      # reemplazamos a con c.
        a_fijo = False
    else:                          # Si no, entonces f(b) y f(c) son del
        fb = fc                    # mismo signo. Reemplazamos f(b) con f(c)
        b = c                      # y también reemplazamos b con c.
        b_fijo = False
    c = nueva_c(a, b, fa, fb)      # Actualizamos el valor de c de acuerdo a los nuevos valores.
    fc = f(c)                      # Evaluamos f(x) con x = c.
    c_values = np.append(c_values, c) # Añadimos el valor c_i al arreglo.
    fc_values = np.append(fc_values, fc) # Añadimos el valor f(c_i) al arreglo.
    print("Iteración", i, ": a =", f"{a:3.5f}", "b =", f"{b:3.5f}", "c =", f"{c:3.5f}", "f(a) =", f"{fa:3.5f}", "f(b) =", f"{fb:3.5f}", "f(c) =", f"{fc:3.5f}")

print("Solución: x =", c)

if a_fijo:
    pf = a
    fpf = fa
if b_fijo:
    pf = b
    fpf = fb

fig, axs = plt.subplots()
axs.set_xlabel('x')
axs.set_ylabel('y')
fig.suptitle('Falsa posición')

axs.plot(x, y, label=r'$x^2 - xe^x + 4$', color='blue')
axs.plot(c, fc, 'o', label=r'Sol. aproximada: $x = $'+np.format_float_positional(c, precision=5), color='purple')

axs.grid('on')
for n, m in np.nditer([c_values, fc_values]):
    axs.axline((n, m), (pf, fpf), color='red', linestyle=':', linewidth=0.5)
axs.axline((c_values[c_values.size - 1], fc_values[fc_values.size - 1]), (pf, fpf), color='purple', linestyle=':', linewidth=0.5)

handles, labels = axs.get_legend_handles_labels()
proxy_rojo = mlines.Line2D([], [], color='red', linestyle=':', linewidth=0.5)
handles.append(proxy_rojo)
if a_fijo:
    labels.append(r'Rectas $\overline{(c_n, f(c_n)), (a, f(a))}$')
if b_fijo:
    labels.append(r'Rectas $\overline{(c_n, f(c_n)), (b, f(b))}$')
axs.legend(handles=handles, labels=labels, loc='lower left')

plt.show()
