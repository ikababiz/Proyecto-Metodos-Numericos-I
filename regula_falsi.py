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
COMBO_FUNCION = "comboFuncion"
BTN_CALCULAR = "calcularbutton"
BTN_TABLA = "tablabutton"
BTN_GRAFICA = "graficabutton"
BTN_VOLVER = "unidad2button"


def calcular_regula_falsi(f, a, b, epsilon=EPSILON, max_iter=200):
    a, b = float(a), float(b)
    if a >= b:
        raise ValueError("Error, el valor de a debe ser menor que b")
    fa, fb = f(a), f(b)
    if (fa > 0) == (fb > 0):
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


class MetodoFalsaPosicion(QWidget):
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

        self.funciones_disponibles = \
        {
                0: (lambda x: x ** 2 - x * np.exp(x) + 4,  # lamda pueden generar overflow en consola
                    r'$x^2 - x e^x + 4$'),
                1: (lambda x: -10 * np.exp(-x / 2) * np.cos(2 * x),
                    r'$-10e^{-x/2} \cos(2x)$'),
                2: (lambda x: x ** 2 - np.exp(x) - 3 * x + 2,
                    r'$x^2 - e^x - 3x + 2$')
        }  # funciones de clases, tareas y examen

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

    def obtener_funcion_actual(self):
        # ;ee el índice seleccionado en el ComboBox y devuelve (funcion, etiqueta)
        idx = self.widget(COMBO_FUNCION).currentIndex()
        return self.funciones_disponibles.get(idx, self.funciones_disponibles[0])

    def leer_filas(self): # evalua usando calcular_regula_falsi y regresa filas
        try:
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())
            func, _ = self.obtener_funcion_actual()
            return calcular_regula_falsi(func, a, b)
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos.", str(e))
            return None

    def calcular(self):
        filas = self.leer_filas()
        if not filas:
            return

        n, a_final, b_final, c, fa, fb, fc = filas[-1] # la ultima fila
        if n >= 199:
            QMessageBox.warning(
                self, "Aviso de convergencia",
                f"El método se detuvo tras {n} iteraciones sin converger bajo la tolerancia esperada.\n"
                f"Último valor calculado: {c:.4f}\n"
                "Revisa la tabla o la gráfica para analizar el comportamiento."
            )
        else: # converge
            QMessageBox.information(
                self, "Resultado",
                f"La raíz aproximada es {c:.4f}\n"
                f"Número de iteraciones: {n}\n"
            )  # el resultado

    # por ahora no hace nada mas que graficar una misma funcion
    def abrir_grafica(self):
        filas = self.leer_filas()  # reusa filas para calcular dependiendo de la funcion
        if not filas:
            return

        try:
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())
            func, label_latex = self.obtener_funcion_actual()

            # igual que en otros metodos se extrae de filas
            a_inicial = filas[0][1]
            b_inicial = filas[0][2]
            c_final = filas[-1][3]

            # fa = f(a)
            # fb = f(b)
            #
            # c = nueva_c(a, b, fa, fb)
            # fc = f(c)
            # c_values = np.array([c])  # Arreglo con los valores de c_n.
            # fc_values = np.array([fc])  # Arreglo con los valores de f(c_n).

            x = np.linspace(a, b, 200)  # Dominio de la gráfica.
            y = func(x) # Expresión a dibujar en la gráfica.

            # a_fijo = True
            # b_fijo = True
            #
            #
            # if a_fijo:
            #     pf = a
            #     fpf = fa
            # if b_fijo:
            #     pf = b
            #     fpf = fb

            fig, axs = plt.subplots()
            axs.set_xlabel('x')
            axs.set_ylabel('y')
            fig.suptitle('Falsa posición')

            axs.plot(x, y, label=label_latex, color='blue')
            axs.plot(c_final, 0, 'o', label=r'Sol. aproximada: $x = $' + np.format_float_positional(c_final, precision=4),
                     color='purple')

            axs.grid('on')

            for fila in filas[:-1]:
                n, a, b, c, fa, fb, fc = fila

                axs.plot([a, b], [fa, fb], color='red', linestyle=':', linewidth=0.8)
                axs.plot(c, 0, color='green', marker='^', markersize=5)
                axs.plot([c, c], [0, fc], color='green', linestyle=':', linewidth=0.5)

            handles, labels = axs.get_legend_handles_labels()
            proxy_secante = mlines.Line2D([], [], color='red', linestyle=':', linewidth=0.8)
            proxy_c = mlines.Line2D([], [], color='green', marker='^', linestyle='None')

            handles.extend([proxy_secante, proxy_c]) #
            labels.extend(['Rectas secantes', r'Aproximaciones $c_n$'])
            axs.legend(handles=handles, labels=labels, loc='lower left')

            plt.show()


        except Exception as e:
            QMessageBox.warning(self, "Error al graficar.", str(e))
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
    w = MetodoFalsaPosicion()
    w.show()
    sys.exit(app.exec())
