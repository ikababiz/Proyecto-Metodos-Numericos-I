#!/bin/python3

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import sympy as sp
import math

x = sp.symbols('x')
deriv = sp.diff(x**2 - x*sp.E**x + 4)

def f(x):
    return x**2 - x*math.exp(x) + 4

def df(n):
    return deriv.evalf(subs={x:n})

def print_values(i, x, fx, dfx):
    print("Iteración "+str(i)+" : x_"+str(i)+" =", f"{x:3.5f}", "f(x_"+str(i)+") =", f"{fx:3.5f}", "df(x_"+str(i)+") =", f"{dfx:3.5f}")

x_i = 0
x_aux = x_i
fx_i = f(x_i)
dfx_i = df(fx_i)

xi_values   = np.array([x_i])
xaux_values = np.array([x_i])
fxi_values  = np.array([fx_i])

i = 1
print_values(i, x_i, fx_i, dfx_i)
while i < 10:
    i += 1
    if dfx_i == 0:
        print("Indeterminación\n")
        exit(1)
    x_i = x_aux - fx_i/dfx_i
    fx_i = f(x_i)
    dfx_i = df(x_i)
    print_values(i, x_i, fx_i, dfx_i)
    x_aux = x_i
    xi_values   = np.append(xi_values, x_i)
    xaux_values = np.append(xaux_values, x_aux)
    fxi_values  = np.append(fxi_values, fx_i)

fig, axs = plt.subplots()
axs.set_xlabel('x')
axs.set_ylabel('y')
fig.suptitle('Método de Newton')

print(xi_values)
print(xaux_values)
print(fxi_values)

xi_values   = np.array(xi_values, dtype=float)
xaux_values = np.array(xaux_values, dtype=float)
fxi_values  = np.array(fxi_values, dtype=float)

xp = np.linspace(-4, 4)
yp = xp**2 - xp*np.exp(xp) + 4

axs.plot(xp, yp, label=r'$x^2 - xe^x + 4$', color='blue')
axs.plot(x_i, fx_i, marker='o', label=r'Sol. aproximada: $x = $'+format(x_i, '.5f'), color='purple')

axs.grid('on')
tam = xi_values.size
for i in range(1, tam - 2):
    axs.axline((xi_values[i+1], 0), (xi_values[i], fxi_values[i]), color='red', linestyle=':', linewidth=0.5)
    plt.plot([xi_values[i], xi_values[i]], [fxi_values[i], 0], color='g', linestyle=':')
    axs.plot(xi_values[i], fxi_values[i], color='g', marker='^')
    axs.plot(xi_values[i], 0, color='g', marker='s')
axs.axline((xi_values[tam - 1], 0), (xi_values[tam - 2], fxi_values[tam - 2]), color='purple', label='Tangente aprox. a la solución', linestyle=':', linewidth=0.5)

handles, labels = axs.get_legend_handles_labels()
proxy_rojo = mlines.Line2D([], [], color='red', linestyle=':', linewidth=0.5)
proxy_verde_uno = mlines.Line2D([], [], color='green', marker='s')
proxy_verde_dos = mlines.Line2D([], [], color='green', marker='^')
proxy_verde_tres = mlines.Line2D([], [], color='green', linestyle=':', linewidth=0.5)
handles.append(proxy_rojo)
handles.append(proxy_verde_uno)
handles.append(proxy_verde_dos)
handles.append(proxy_verde_tres)
labels.append('Rectas tangentes')
labels.append(r'Puntos $(x_{n+1}, 0)$')
labels.append(r'Puntos $(x_n, f(x_n))$')
labels.append(r'Rectas $\overline{(x_n, f(x_n)), (x_{n+1}, 0)}$')
axs.legend(handles=handles, labels=labels, loc='lower left')

plt.show()
