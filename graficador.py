import sys

import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDoubleSpinBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget,
)
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations,
)

# permite escribir "2x", "x^2" y "sin x" además de "2*x", "x**2"
TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application, convert_xor,
)
x = sp.Symbol("x")


class Graficador(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graficador de funciones")
        self.resize(900, 600)

        # ---- controles ----
        self.entrada = QLineEdit("x^2 - x*exp(x) + 4")
        self.entrada.setPlaceholderText("Escribe f(x), por ejemplo: sin(x)/x")
        self.xmin = QDoubleSpinBox()
        self.xmax = QDoubleSpinBox()
        for caja, valor in ((self.xmin, -5), (self.xmax, 5)):
            caja.setRange(-1e6, 1e6)
            caja.setDecimals(2)
            caja.setValue(valor)
        self.chk_derivada = QCheckBox("Mostrar derivada")
        self.boton = QPushButton("Graficar")
        self.mensaje = QLabel("")

        fila = QHBoxLayout()
        fila.addWidget(QLabel("f(x) ="))
        fila.addWidget(self.entrada, stretch=1)
        fila.addWidget(QLabel("x mín:"))
        fila.addWidget(self.xmin)
        fila.addWidget(QLabel("x máx:"))
        fila.addWidget(self.xmax)
        fila.addWidget(self.chk_derivada)
        fila.addWidget(self.boton)

        # ---- gráfica ----
        self.grafica = pg.PlotWidget()
        self.grafica.showGrid(x=True, y=True)
        self.grafica.addLegend()
        self.grafica.addLine(y=0, pen=pg.mkPen("k", width=1))  # eje x
        self.grafica.addLine(x=0, pen=pg.mkPen("k", width=1))  # eje y

        centro = QWidget()
        layout = QVBoxLayout(centro)
        layout.addLayout(fila)
        layout.addWidget(self.grafica, stretch=1)
        layout.addWidget(self.mensaje)
        self.setCentralWidget(centro)

        # ---- eventos ----
        self.boton.clicked.connect(self.graficar)
        self.entrada.returnPressed.connect(self.graficar)
        self.graficar()

    def evaluar(self, expr, xs):
        """Convierte una expresión de SymPy en valores numéricos."""
        f = sp.lambdify(x, expr, modules="numpy")
        with np.errstate(all="ignore"):
            ys = np.asarray(f(xs), dtype=complex)
        ys = np.broadcast_to(ys, xs.shape).astype(complex)
        # se descartan puntos fuera del dominio (complejos o infinitos)
        ys = np.where(np.abs(ys.imag) < 1e-12, ys.real, np.nan)
        return np.where(np.isfinite(ys), ys, np.nan)

    def graficar(self):
        self.grafica.clear()
        self.grafica.addLine(y=0, pen=pg.mkPen("k", width=1))
        self.grafica.addLine(x=0, pen=pg.mkPen("k", width=1))

        a, b = self.xmin.value(), self.xmax.value()
        if a >= b:
            self.mensaje.setText("Error: x mín debe ser menor que x máx.")
            return
        try:
            expr = parse_expr(self.entrada.text(), transformations=TRANSFORMACIONES,
                              local_dict={"x": x})
            xs = np.linspace(a, b, 2000)
            ys = self.evaluar(expr, xs)
            self.grafica.plot(xs, ys, pen=pg.mkPen("b", width=2),
                              name="f(x)", connect="finite")

            if self.chk_derivada.isChecked():
                deriv = sp.diff(expr, x)
                self.grafica.plot(xs, self.evaluar(deriv, xs),
                                  pen=pg.mkPen("r", width=2, style=pg.QtCore.Qt.DashLine),
                                  name="f'(x)", connect="finite")
                texto = f"f(x) = {expr}     f'(x) = {deriv}"
            else:
                texto = f"f(x) = {expr}"
            self.mensaje.setText(texto)
        except Exception as e:
            self.mensaje.setText(f"No se pudo interpretar la función: {e}")


def main():
    app = QApplication(sys.argv)
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    ventana = Graficador()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
