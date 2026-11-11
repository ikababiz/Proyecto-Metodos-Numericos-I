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

EPSILON = 1e-6  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
ENCABEZADOS = ["n", "x_n", "f(x_n)"] # cada metodo llevara su encabezado

# para otros metodos en Qt Designer los objetnames se cambian solo aqui
LINE_XC = "lineEditXc"
LINE_XU = "lineEditXu"
BTN_CALCULAR = "calcularbutton"
BTN_TABLA = "tablabutton"
BTN_VOLVER = "unidad2button"

def f(x):
    return x**2 - x*math.exp(x) + 4

def xi(xc, xu, fc, fu):
    faux = fu - fc
    if abs(faux) < EPSILON:
        return xu, False
    return xu - fu*(xu-xc)/(faux), True

def calcular_secante(x_c, x_u, max_iter=200):
    xc = float(x_c)
    xu = float(x_u)
    if x_c == x_u:
        exit(1)
    filas = []
    fc = f(xc)
    fu = f(xu)

    filas.append((1, x_c, fc))
    filas.append((2, x_u, fu))

    xaux, _ = xi(xc, xu, fc, fu)
    faux = f(xaux)

    i = 3
    still = True
    while still and i < max_iter:
        filas.append((i, xaux, faux))
        xc = xu
        fc = fu
        xu = xaux
        fu = faux
        xaux, still = xi(xc, xu, fc, fu)
        faux = f(xaux)
        i += 1
    return filas

def cargar_ui(nombre): # metodo de carga generico
    file = QFile(str(CARPETA_UI / f"{nombre}.ui"))
    if not file.open(QFile.ReadOnly): # lectura
        raise FileNotFoundError(f"No se encontró {nombre}.ui en {CARPETA_UI}")
    widget = QUiLoader().load(file)
    file.close()
    return widget


class MetodoSecante(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de la Secante")
        self.resize(800, 600)

        self.ui = cargar_ui("Secante")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (tabla, gráfica) para que Qt no las cierre

        self.widget(BTN_CALCULAR).clicked.connect(self.calcular)
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
            x_c = float(self.widget(LINE_XC).text())
            x_u = float(self.widget(LINE_XU).text())
            return calcular_secante(x_c, x_u)
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None

    def calcular(self):
        filas = self.leer_filas()
        if not filas:
            return

        n, x_final, fx_final = filas[-1] # la ultima fila
        QMessageBox.information(
            self, "Resultado",
            f"La raíz aproximada es {x_final:.4f}\n"
            f"Número de iteraciones: {n}\n"
        ) # el resultado


    def abrir_tabla(self):
        filas = self.leer_filas()
        if not filas:
            return
        w2 = VentanaTabla("Método de la Secante", ENCABEZADOS, filas)
        self.windows.append(w2)
        w2.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = MetodoSecante()
    w.show()
    sys.exit(app.exec())
