from pathlib import Path
import sys

from PySide6.QtCore import Signal # esta cosa se necesita para mandar una señal para que MenuPrincipal sepa que hacer
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QVBoxLayout,  QWidget,
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader

import math
from PySide6.QtWidgets import QMainWindow

from Tabla_resultados import VentanaTabla
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import sympy as sp

EPSILON = 1e-6  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
ENCABEZADOS = ["n", "x_n", "f(x_n)", "f'(x_n)"] # cada metodo llevara su encabezado

# para otros metodos en Qt Designer los objetnames se cambian solo aqui
LINE_X = "lineEditX"
BTN_CALCULAR = "calcularbutton"
BTN_TABLA = "tablabutton"
BTN_GRAFICA = "graficabutton"
BTN_VOLVER = "unidad2button"

x = sp.symbols('x')
deriv = sp.diff(x**2 - x*sp.E**x + 4)


def f(x):
    return x**2 - x*math.exp(x) + 4


def df(n):
    return float(deriv.evalf(subs={x:n}))


def calcular_newton(x_i, epsilon=EPSILON, max_iter=200):
    x_i = float(x_i)
    x_aux = 0
    i = 1
    filas = []
    while i < max_iter:
        fx_i = f(x_i)
        dfx_i = df(x_i)
        filas.append((i, x_i, fx_i, dfx_i))
        if dfx_i == 0 or abs(x_i - x_aux) < epsilon:
            break
        x_aux = x_i
        x_i = x_aux - fx_i/dfx_i
        i += 1
    return filas


def cargar_ui(nombre): # metodo de carga generico
    file = QFile(str(CARPETA_UI / f"{nombre}.ui"))
    if not file.open(QFile.ReadOnly): # lectura
        raise FileNotFoundError(f"No se encontró {nombre}.ui en {CARPETA_UI}")
    widget = QUiLoader().load(file)
    file.close()
    return widget


class MetodoNewton(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de Newton")
        self.resize(800, 600)

        self.ui = cargar_ui("Newton")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (tabla, gráfica) para que Qt no las cierre

        self.widget(BTN_CALCULAR).clicked.connect(self.calcular)
        self.widget(BTN_GRAFICA).clicked.connect(self.abrir_grafica)
        self.widget(BTN_TABLA).clicked.connect(self.abrir_tabla)

        self.widget(BTN_VOLVER).clicked.connect(self.volver.emit) #manda la señal a MenuPrincipal


    def widget(self, nombre):  # busca el nombre del widget en el disenio
        widg = self.ui.findChild(QWidget, nombre)
        if widg is None:
            existentes = [c.objectName() for c in self.ui.findChildren(QWidget)]
            raise LookupError(
                f"No hay un widget llamado '{nombre}'. "
                f"Lista de widgets: {existentes}")
        return widg

    def leer_filas(self): # evalua usando calcular_biseccion y regresa filas
        try:
            x_i = float(self.widget(LINE_X).text())
            return calcular_newton(x_i)
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None

    def calcular(self):
        filas = self.leer_filas()
        if not filas:
            return

        n, x_final, fx_final, dfx_final = filas[-1] # la ultima fila
        QMessageBox.information(
            self, "Resultado",
            f"La raíz aproximada es {x_final:.4f}\n"
            f"Número de iteraciones: {n}\n"
        ) # el resultado

    # por ahora no hace nada mas que graficar una misma funcion
    def abrir_grafica(self):
        # w3 = Graficador()  # del archivo graficador.py, la clase que hace la grafica
        # self.windows.append(w3)  # se guarda para que Qt no la cierre
        # w3.show()
        try:
            x_i = float(self.widget(LINE_X).text())
            x_aux = x_i
            fx_i = f(x_i)
            dfx_i = df(fx_i)

            xi_values   = np.array([x_i])
            xaux_values = np.array([x_i])
            fxi_values  = np.array([fx_i])

            i = 1
            while i < 10:
                i += 1
                if dfx_i == 0:
                    break
                x_i = x_aux - fx_i/dfx_i
                fx_i = f(x_i)
                dfx_i = df(x_i)
                x_aux = x_i
                xi_values   = np.append(xi_values, x_i)
                xaux_values = np.append(xaux_values, x_aux)
                fxi_values  = np.append(fxi_values, fx_i)

            fig, axs = plt.subplots()
            axs.set_xlabel('x')
            axs.set_ylabel('y')
            fig.suptitle('Método de Newton')

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

        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None


    def abrir_tabla(self):
        filas = self.leer_filas()
        if not filas:
            return
        w2 = VentanaTabla("Método de Newton", ENCABEZADOS, filas)
        self.windows.append(w2)
        w2.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = MetodoNewton()
    w.show()
    sys.exit(app.exec())
