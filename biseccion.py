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

from graficador import Graficador
from Tabla_resultados import VentanaTabla

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
def funcion(x): # la del ejemplo
    return x**2 - x * math.exp(x) + 4

def calcular_biseccion(a, b, epsilon=EPSILON, max_iter=200):
        a, b = float(a), float(b)
        if a >= b:
            raise ValueError("Error, el valor de a debe ser menor que b")
        if funcion(a) * funcion(b) >= 0:
            raise ValueError(f"Error, f({a}) y f({b}) deben tener signos distintos")

        filas = []
        n = 1
        while abs(b - a) > epsilon and n < max_iter:
            c = (a + b) / 2
            fa, fb, fc = funcion(a), funcion(b), funcion(c)
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
            a = float(self.widget(LINE_A).text())
            b = float(self.widget(LINE_B).text())
            return calcular_biseccion(a, b)
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
        w3 = Graficador()  # del archivo graficador.py, la clase que hace la grafica
        self.windows.append(w3)  # se guarda para que Qt no la cierre
        w3.show()

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
