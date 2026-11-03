from pathlib import Path
import sys

from PySide6.QtCore import Signal # esta cosa se necesita para mandar una señal para que MenuPrincipal sepa que hacer
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QVBoxLayout,  QWidget,
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader

import math

from Tabla_resultados import VentanaTabla
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np

EPSILON = 1e-6  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
ENCABEZADOS = ["n", "a", "b", "c", "f(a)", "f(b)", "f(c)"] # cada metodo llevara su encabezado

# para otros metodos en Qt Designer los objetnames se cambian solo aqui
LINE_A = "lineEditA"
LINE_B = "lineEditB"
BTN_CALCULAR = "calcularbutton"
BTN_TABLA = "tablabutton"
BTN_GRAFICA = "graficabutton"
BTN_VOLVER = "unidad2button"

# por ahora es estatica
def f(x): # la del ejemplo
    return x**2 - x * math.exp(x) + 4


def nueva_c(a, b, fa, fb):
    return a - (fa*(b-a))/(fb - fa) # Punto (c, 0) para una recta.


def calcular_regula_falsi(a, b, epsilon=EPSILON, max_iter=200):
    a, b = float(a), float(b)
    if a >= b:
        raise ValueError("Error, el valor de a debe ser menor que b")
    if f(a) * f(b) >= 0:
        raise ValueError(f"Error, f({a}) y f({b}) deben tener signos distintos")

    filas = []
    n = 1
    while abs(b - a) > epsilon and n < max_iter: # se puede tomar en consideración otros aspectos
        fa, fb = f(a), f(b)
        # se calcula c (antes de evaluar f(c))
        c = a - fa * (b - a) / (fb - fa)
        fc = f(c)
        filas.append((n, a, b, c, fa, fb, fc))

        if abs(fc) < epsilon:
            break
        if fa * fc > 0:
            a = c
        else:
            b = c
        n += 1
    return filas


def cargar_ui(nombre): # metodo de carga generico
    file = QFile(str(CARPETA_UI / f"{nombre}.ui"))
    if not file.open(QFile.ReadOnly): # lectura
        raise FileNotFoundError(f"No se encontró {nombre}.ui en {CARPETA_UI}")
    widget = QUiLoader().load(file)
    file.close()
    return widget


class MetodoBiseccion(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método Falsa Posición")
        self.resize(800, 600)

        self.ui = cargar_ui("RegulaFalsi")
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

    def leer_filas(self): # evalua usando calcular_regula_falsi y regresa filas
        try:
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())
            return calcular_regula_falsi(a, b)
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None

    def calcular(self):
        filas = self.leer_filas()
        if not filas:
            return

        n, a_final, b_final, c, fa, fb, fc = filas[-1] # la ultima fila
        QMessageBox.information(
            self, "Resultado",
            f"La raíz aproximada es {c:.4f}\n"
            f"Número de iteraciones: {n}\n"
        ) # el resultado

    # por ahora no hace nada mas que graficar una misma funcion
    def abrir_grafica(self):
        # w3 = Graficador()  # del archivo graficador.py, la clase que hace la grafica
        # self.windows.append(w3)  # se guarda para que Qt no la cierre
        # w3.show()
        try:
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())

            fa = f(a)
            fb = f(b)

            c = nueva_c(a, b, fa, fb)
            fc = f(c)
            c_values = np.array([c])  # Arreglo con los valores de c_n.
            fc_values = np.array([fc])  # Arreglo con los valores de f(c_n).

            x = np.linspace(a, b)  # Dominio de la gráfica.
            y = x ** 2 - x * np.exp(x) + 4  # Expresión a dibujar en la gráfica.

            epsilon = EPSILON  # Diferencia mínima.

            a_fijo = True
            b_fijo = True

            i = 1
            if a >= b:
                raise ValueError("Error, el valor de a debe ser menor que b")
            if np.sign(fa) == np.sign(fb):  # Si f(a) y f(b) son del mismo signo, aborta el programa.
                #print("La solución no es posible en el rango dado\n")
                raise ValueError(f"Error, f({a}) y f({b}) deben tener signos distintos")
            while abs(fc) > epsilon:   # Iterar hasta que la distancia entre f(c) y la recta x sea menor a epsilon.
                i += 1  # Seguir la iteración.
                if np.sign(fa) == np.sign(fc):  # Si f(a) y f(c) son del mismo signo,
                    fa = fc  # reemplazamos f(a) con f(c) y también
                    a = c  # reemplazamos a con c.
                    a_fijo = False
                else:  # Si no, entonces f(b) y f(c) son del
                    fb = fc  # mismo signo. Reemplazamos f(b) con f(c)
                    b = c  # y también reemplazamos b con c.
                    b_fijo = False
                c = nueva_c(a, b, fa, fb)  # Actualizamos el valor de c de acuerdo a los nuevos valores.
                fc = f(c)  # Evaluamos f(x) con x = c.
                c_values = np.append(c_values, c)  # Añadimos el valor c_i al arreglo.
                fc_values = np.append(fc_values, fc)  # Añadimos el valor f(c_i) al arreglo.

            #print("Solución aproximada: x = ", c)

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
            axs.plot(c, fc, 'o', label=r'Sol. aproximada: $x = $' + np.format_float_positional(c, precision=5),
                     color='purple')

            axs.grid('on')
            for n, m in np.nditer([c_values, fc_values]):
                axs.axline((n, m), (pf, fpf), color='red', linestyle=':', linewidth=0.5)
            axs.axline((c_values[c_values.size - 1], fc_values[fc_values.size - 1]), (pf, fpf), color='purple',
                       linestyle=':', linewidth=0.5)

            handles, labels = axs.get_legend_handles_labels()
            proxy_rojo = mlines.Line2D([], [], color='red', linestyle=':', linewidth=0.5)
            handles.append(proxy_rojo)
            if a_fijo:
                labels.append(r'Rectas $\overline{(c_n, f(c_n)), (a, f(a))}$')
            if b_fijo:
                labels.append(r'Rectas $\overline{(c_n, f(c_n)), (b, f(b))}$')
            axs.legend(handles=handles, labels=labels, loc='lower left')

            plt.show()

        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None


    def abrir_tabla(self):
        filas = self.leer_filas()
        if not filas:
            return
        w2 = VentanaTabla("Método Regula Falsi", ENCABEZADOS, filas)
        self.windows.append(w2)
        w2.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = MetodoBiseccion()
    w.show()
    sys.exit(app.exec())