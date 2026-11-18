from pathlib import Path
import sys
import Imagenes_rc

from PySide6.QtCore import Signal # esta cosa se necesita para mandar una señal para que MenuPrincipal sepa que hacer
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QVBoxLayout,  QWidget,
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader

import math
from PySide6.QtWidgets import QMainWindow

from Tabla_resultados import VentanaTabla
import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines # para el empaquetado del .exe
import numpy as np

EPSILON = 1e-5  # valor muy pequeño > 0, sale igual que las tablas en hoja de calculo

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


def calcular_biseccion(f, a, b, epsilon=EPSILON, max_iter=200): # ahora recibe funcion
        a, b = float(a), float(b)
        if a >= b:
            raise ValueError("Error, el valor de a debe ser menor que b.")
        try:
            fa = f(a)
            fb = f(b)
        except OverflowError:
            raise ValueError("Error, el intervalo es excesivamente grande y causa overflow.")
        if (fa > 0) == (fb > 0):
            raise ValueError(f"Error, f({a}) y f({b}) deben tener signos distintos.")

        filas = []
        n = 1
        while abs(b - a) > epsilon and n < max_iter:
            c = (a + b) / 2
            fa, fb, fc = f(a), f(b), f(c)
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

        self.setWindowTitle("Método de bisección")
        self.resize(800, 600)

        self.ui = cargar_ui("Biseccion")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (tabla, gráfica) para que Qt no las cierre

        self.funciones_disponibles = \
        {
            0: (lambda x: x ** 2 - x * np.exp(x) + 4, # lamda pueden generar overflow en consola
                r'$x^2 - x e^x + 4$'),
            1: (lambda x: -10 * np.exp(-x / 2) * np.cos(2 * x),
                r'$-10e^{-x/2} \cos(2x)$'),
            2: (lambda x: x ** 2 - np.exp(x) - 3 * x + 2,
                r'$x^2 - e^x - 3x + 2$')
        } # funciones de clases, tareas y examen

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

    def leer_filas(self): # evalua usando calcular_biseccion y regresa filas
        try:
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())
            func, _ = self.obtener_funcion_actual()
            return calcular_biseccion(func, a, b)
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
        else:  # converge
            QMessageBox.information(
                self, "Resultado",
                f"La raíz aproximada es {c:.4f}\n"
                f"Número de iteraciones: {n}\n"
            )  # el resultado

    # por ahora no hace nada mas que graficar una misma funcion
    def abrir_grafica(self):
        filas = self.leer_filas() # reusa filas para calcular dependiendo de la funcion
        if not filas:
            return

        try:
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())
            func, label_latex = self.obtener_funcion_actual() # para tener la funcion y el label

            c_values = np.array([fila[3] for fila in filas])  # Arreglo con los valores de c_n.
            c = c_values[-1] # usa los valores obtenidos en filas
            fc = filas[-1][6] # usa los valores obtenidos en filas

            x = np.linspace(a, b, 200) # Dominio de la gráfica.
            y = func(x)

            fig, axs = plt.subplots()
            axs.set_xlabel('x')
            axs.set_ylabel('y')
            fig.suptitle('Bisección')

            axs.plot(x, y, label=label_latex, color='blue') # label dinamico
            axs.plot(c, fc, 'o', label='Sol. aproximada: $x = $' + np.format_float_positional(c, precision=4), # para que coincida
                     color='purple')

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

        except Exception as e:
            QMessageBox.warning(self, "Error al graficar.", str(e))
            return None


    def abrir_tabla(self):
        filas = self.leer_filas()
        if not filas:
            return
        w2 = VentanaTabla("Método de Bisección", ENCABEZADOS, filas)
        self.windows.append(w2)
        w2.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoBiseccion()
    w.show()
    sys.exit(app.exec())
