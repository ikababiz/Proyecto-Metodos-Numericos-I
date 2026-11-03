#!/bin/python3

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np

def f(x):
    return x**2 - x*np.exp(x) + 4

# Rango inicial [a, b].
a = -3
b =  3
temp_a = a
temp_b = b
c = (a + b)/2 # La media aritmética en el rango dado.
c_values = np.array([c]) # Arreglo con los valores de c_n.

fa = f(a)
fb = f(b)
fc = f(c)

x = np.linspace(a, b)      # Dominio de la gráfica.
y = x**2 - x*np.exp(x) + 4 # Expresión a dibujar en la gráfica.

epsilon = 0.001 # Diferencia mínima.

i = 1
print("Iteración", i, ": a =", f"{a:3.5f}", "b =", f"{b:3.5f}", "c =", f"{c:3.5f}", "f(a) =", f"{fa:3.5f}", "f(b) =", f"{fb:3.5f}", "f(c) =", f"{fc:3.5f}")
if np.sign(fa) == np.sign(fb): # Si f(a) y f(b) son del mismo signo, aborta el programa.
    print("La solución no es posible en el rango dado\n")
    exit(1)
while abs(b - a) > epsilon: # Iterar hasta que la diferencia de los valores del rango sea menor a epsilon.
    i += 1 # Seguir la iteración.
    if np.sign(fa) == np.sign(fc): # Si f(a) y f(c) son del mismo signo,
        fa = fc                    # reemplazamos f(a) con f(c) y también
        a = c                      # reemplazamos a con c.
    else:                          # Si no, entonces f(b) y f(c) son del
        fb = fc                    # mismo signo. Reemplazamos f(b) con f(c)
        b = c                      # y también reemplazamos b con c.
    c = (a + b)/2 # Actualizamos el valor de c de acuerdo al nuevo rango.
    fc = f(c)     # Evaluamos f(x) con x = c.
    c_values = np.append(c_values, c) # Añadimos el valor c_i al arreglo.
    print("Iteración", i, ": a =", f"{a:3.5f}", "b =", f"{b:3.5f}", "c =", f"{c:3.5f}", "f(a) =", f"{fa:3.5f}", "f(b) =", f"{fb:3.5f}", "f(c) =", f"{fc:3.5f}")

print("Solución aproximada: x = ", c)

fig, axs = plt.subplots()
axs.set_xlabel('x')
axs.set_ylabel('y')
fig.suptitle('Bisección')

axs.plot(x, y, label=r'$x^2 - xe^x + 4$', color='blue')
axs.plot(c, fc, 'o', label='Sol. aproximada: $x = $'+np.format_float_positional(c, precision=5), color='purple')

axs.grid('on')
ticks = axs.set_xticks(c_values)
for n in range(len(ticks) - 1):
    ticks[n].label1.set_color("red")
    ticks[n].tick1line.set_markeredgecolor("red")
    ticks[n].gridline.set(visible=True, linestyle=':', linewidth=0.5, color='red')
ticks[len(ticks) - 1].label1.set_color("purple")
ticks[len(ticks) - 1].tick1line.set_markeredgecolor("purple")
ticks[len(ticks) - 1].gridline.set(visible=True, linestyle=':', linewidth=0.5, color='purple')

handles, labels = axs.get_legend_handles_labels()
proxy_rojo = mlines.Line2D([], [], color='red', linestyle=':', linewidth=0.5)
handles.append(proxy_rojo)
labels.append('Aproximaciones $c_n$')
axs.legend(handles=handles, labels=labels, loc='lower left')

plt.show()
