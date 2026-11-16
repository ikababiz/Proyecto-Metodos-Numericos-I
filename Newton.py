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

EPSILON = 1e-5  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
ENCABEZADOS = ["n", "x_n", "f(x_n)", "f'(x_n)"] # cada metodo llevara su encabezado

# para otros metodos en Qt Designer los objetnames se cambian solo aqui
LINE_X = "lineEditX"
COMBO_FUNCION = "comboFuncion"
BTN_CALCULAR = "calcularbutton"
BTN_TABLA = "tablabutton"
BTN_GRAFICA = "graficabutton"
BTN_VOLVER = "unidad2button"

x_sym = sp.symbols('x')
#deriv = sp.diff(x**2 - x*sp.E**x + 4)
# no creo que sea posible dejarlo como global, quizas un nuevo metodo para calcular la derivada sea necesario
# se reemplaza con derivacion simbplica de SymPy

def calcular_newton(f, df, x_i, epsilon=EPSILON, max_iter=200):
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

        self.funciones_disponibles = \
        {
            0: (x_sym ** 2 - x_sym * sp.exp(x_sym) + 4,
                r'$x^2 - x e^x + 4$'),
            1: (-10 * sp.exp(-x_sym / 2) * sp.cos(2 * x_sym),
                r'$-10e^{-x/2} \cos(2x)$'),
            2: (x_sym ** 2 - sp.exp(x_sym) - 3 * x_sym + 2,
                r'$x^2 - e^x - 3x + 2$')
        } # para Newton se necesita SymPy

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

    def funciones_numericas(self):
        fun, label_latex = self.obtener_funcion_actual()

        deriv_expr = sp.diff(fun, x_sym) # calcula la derivada simbolicamente
        # lambdify para convertirlas en expresiones numericas de numpy
        f_num = sp.lambdify(x_sym, fun, 'numpy')
        df_num = sp.lambdify(x_sym, deriv_expr, 'numpy')

        return f_num, df_num, label_latex # regresa la funcion, la derivada y la etiqueta

    def leer_filas(self): # evalua usando calcular_biseccion y regresa filas
        try:
            x_i = float(self.widget(LINE_X).text()) # ahora se evalua dependiendo de la funcion
            f_num, df_num, _ = self.funciones_numericas()
            return calcular_newton(f_num, df_num, x_i)
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None

    def calcular(self):
        filas = self.leer_filas()
        if not filas:
            return

        n, x_final, fx_final, dfx_final = filas[-1] # la ultima fila
        if n >= 199:
            QMessageBox.warning(
                self, "Aviso de convergencia",
                f"El método se detuvo tras {n} iteraciones sin converger bajo la tolerancia esperada.\n"
                f"Último valor calculado: {x_final:.4f}\n"
                "Revisa la tabla o la gráfica para analizar el comportamiento."
            )
        else:  # converge
            QMessageBox.information(
                self, "Resultado",
                f"La raíz aproximada es {x_final:.4f}\n"
                f"Número de iteraciones: {n}\n"
            )  # el resultado

    # por ahora no hace nada mas que graficar una misma funcion
    def abrir_grafica(self):
        filas = self.leer_filas()
        if not filas:
            return

        try:
            x_i = float(self.widget(LINE_X).text())
            f_num, df_num, label_latex = self.funciones_numericas()

            x_aux = x_i
            fx_i = f_num(x_i)
            #dfx_i = df(fx_i)

            xi_values   = np.array([fila[1] for fila in filas])
            xaux_values = np.array([x_i])
            fxi_values  = np.array([fila[2] for fila in filas])

            x_final = xi_values[-1]
            fx_final = fxi_values[-1]

            fig, axs = plt.subplots()
            axs.set_xlabel('x')
            axs.set_ylabel('y')
            fig.suptitle('Método de Newton')

            xi_values   = np.array(xi_values, dtype=float)
            xaux_values = np.array(xaux_values, dtype=float)
            fxi_values  = np.array(fxi_values, dtype=float)

            xp = np.linspace(x_final - 4, x_final + 4, 200) # dominio centrado en la raiz
            yp = f_num(xp)

            axs.plot(xp, yp, label=label_latex, color='blue')
            axs.plot(x_final, fx_final, marker='o', label=r'Sol. aproximada: $x = $'+format(x_i, '.4f'), color='purple')

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

        except Exception as e:
            QMessageBox.warning(self, "Error al graficar.", str(e))
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
