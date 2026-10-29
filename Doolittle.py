import random
from pathlib import Path
import sys

import io
import shutil

from PySide6.QtCore import Signal # esta cosa se necesita para mandar una señal para que MenuPrincipal sepa que hacer
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QVBoxLayout, QWidget, QDialog, QLabel, QDialogButtonBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QPixmap # para imagenes
from PySide6.QtUiTools import QUiLoader
import sympy as sp
import numpy as np
from scipy.linalg import lu
from sympy import symbols, Matrix, preview, linsolve
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations,
)

EPSILON = 1e-6  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
# para otros metodos en Qt Designer los objetnames se cambian solo aqui
R_DOOLITTLE = "DoolittleRadio"
R_CROUT = "CroutRadio"
TAMANO = "tamEdit"
MATRIZ = "matButton"
BTN_CALCULAR = "calcButton"
MOSTRAR = "pasosButton"
BTN_VOLVER = "unidad4button"

TAM_MIN, TAM_MAX = 2, 10   # tamanñios de matriz

TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application, convert_xor,
) # sirven para interpretar el texto ingreaso por usuario y pasarlo con las reglas de sintaxis de Python
# i. e. si se escribe 2a + x^2 lo transforma a 2*a + x**2

def cargar_ui(nombre): # metodo de carga generico
    file = QFile(str(CARPETA_UI / f"{nombre}.ui"))
    if not file.open(QFile.ReadOnly): # lectura
        raise FileNotFoundError(f"No se encontró {nombre}.ui en {CARPETA_UI}")
    widget = QUiLoader().load(file)
    file.close()
    return widget

def datos_a_matriz(datos):
    try: # transforma a matrix
        return Matrix([[parse_expr(c, transformations=TRANSFORMACIONES) for c in fila] for fila in datos])
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la matriz: {e}") # si SymPy no logra meter los datos como matrix


def matriz_a_latex(M, aumentada): #Devuelve el LaTeX de la matriz.
    # ahora acepta tanto lista de datos como objeto Matrix de SymPy
    # si aumentada=True dibuja una línea vertical antes de la última columna i. e. [A | b]
    if not isinstance(M, Matrix):
        M = datos_a_matriz(M) # Matrix de SymPy
    if not aumentada: # SymPy latex se encarga de pasar toda la matriz a formato LaTeX correcto
        return sp.latex(M, mat_str="pmatrix", mat_delim=None)
    # en caso de ser aumentada hay que hacerlo 'manual' primero el cuerpo, luego la barra | y al final la columna b
    n = M.cols - 1
    cuerpo = r" \\ ".join(
        " & ".join(sp.latex(M[i, j]) for j in range(M.cols))
        for i in range(M.rows))
    return (r"\left(\begin{array}{" + "c" * n + "|c}" + cuerpo
            + r"\end{array}\right)") # regresa una cadena de texto en formato LaTeX


def latex_a_pixmap(latex, dpi=200):
    # compila el LaTeX con sympy.preview y devuelve un QPixmap (imagen)
    # busca con wich en la terminal para saber donde esta instalado
    if shutil.which("latex") is None or shutil.which("dvipng") is None:
        raise RuntimeError( # validacion que no puedo probar :(
            "Falta LaTeX en esta computadora.")
    buffer = io.BytesIO()
    preview(f"$\\displaystyle {latex}$", output="png", viewer="BytesIO",
            outputbuffer=buffer, euler=False, dvioptions=["-D", str(dpi)])
    pixmap = QPixmap()
    pixmap.loadFromData(buffer.getvalue())
    return pixmap # devuelve la imagen

def FactorizacionLU(M):
    A = np.array(M[:, :-1].tolist(), dtype=float)
    P, L, U = lu(A)

    return L, U # No se que se hace con P

def generar_pasos_detallados(M_orig, metodo):
    M = M_orig.copy() # copia para no perderla
    filas, cols = M.shape
    pasos_lista = [] # para append

    # Matriz inicial
    pasos_lista.append({
        "matriz": M.copy(),
        "operacion": r"\text{Matriz aumentada inicial del sistema}"
    }) # paso 0

    # luego L y U


    return pasos_lista # regresa el conjunto de pasos como texto en formato LaTeX


class VerMatriz(QDialog):
    def __init__(self, datos, parent=None, aumentada=False):
        super().__init__(parent) # no es hija
        self.setWindowTitle("Confirmar matriz")
        # Forzar fondo blanco y texto negro en la ventana emergente
        self.setStyleSheet("background-color: white; color: black;")

        latex = matriz_a_latex(datos, True)  # ValueError si hay celdas inválidas
        pixmap = latex_a_pixmap(latex)  # RuntimeError si falta LaTeX

        imagen = QLabel() # se mete la imagen en un QLabel
        imagen.setPixmap(pixmap)
        imagen.setAlignment(Qt.AlignCenter) # se muestra centrado
        imagen.setStyleSheet("background-color: white;")

        pregunta = QLabel("¿La matriz ingresada es correcta?")
        pregunta.setAlignment(Qt.AlignCenter)
        pregunta.setStyleSheet("color: black; background-color: white;")

        botones = QDialogButtonBox() # boton de confirmacion
        botones.addButton("Sí, continuar", QDialogButtonBox.AcceptRole)
        botones.addButton("No, hacer cambios", QDialogButtonBox.RejectRole)
        botones.accepted.connect(self.accept) # cuando se acepta se cierra
        botones.rejected.connect(self.reject) # sino te deja editar
        botones.setStyleSheet("background-color: #f0f0f0; color: black;")

        layout = QVBoxLayout(self)
        layout.addWidget(imagen)
        layout.addWidget(pregunta)
        layout.addWidget(botones)

class IngresarnaMatriz(QWidget): # falta implementar que si ya hay matriz del mismo tamano la despliege
    conf = Signal(list) # emite senal para canfirmar
    def __init__(self,  n):
        super().__init__()
        self.n = n
        self.setWindowTitle("Ingresar Sistema de Ecuaciones") # elije el tamano minimo posible
        # numero de columnas(n+1), numero de filas + 2 para el inicio encabezado y el final
        self.resize(min(800, 90 * (n + 1)), min(600, 50 * (n + 2))) # tamano dinamico
        # creo que se puede usar self.adjustSize() para tamano dinamico pero no me salio

        self.mat = QTableWidget(n, n+1) # matriz de n x n mas la columna b
        self.mat.setHorizontalHeaderLabels([f"x_{j+1}" for j in range(n)] + ["b"] ) # nombre de columnas
        self.mat.setVerticalHeaderLabels([f"Ec. {i + 1}" for i in range(n)] ) # nombre de cada ecuacion
        self.mat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(n):
            for j in range(n+1):
                celda = QTableWidgetItem("") # vacias al inicio
                celda.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.mat.setItem(i, j, celda) # arma la tabla vacia

        self.info = QLabel(f"Llene la matriz de coeficientes {n}x{n} y la columna b de términos independientes")
        self.info.setWordWrap(True)

        confButton = QPushButton("Confirmar")
        confButton.clicked.connect(self.confirmar)
        # Para pruebas. Porque da hueva escribir matrices
        randButton = QPushButton("RandomFill")
        randButton.clicked.connect(self.random_fill)

        layout = QVBoxLayout(self)
        layout.addWidget(self.mat)
        layout.addWidget(self.info)
        layout.addWidget(randButton)
        layout.addWidget(confButton)

    def confirmar(self):
        datos = self.leer_datos() # al presionar el boton de confirmar se llama  leer_datos
        # validaciones
        for i, fila in enumerate(datos):
            for j, texto in enumerate(fila):
                if texto == "": # si esta vacio
                    self.mat.setCurrentCell(i, j) # highlights (no se como se dice en espanol)
                    QMessageBox.warning(self, "Sistema incompleto", f"La celda a_{i+1}{j+1} está vacía")
                    return

        try: # trata de visualizarla
            vista = VerMatriz(datos, parent=self, aumentada = True)
        except (ValueError, RuntimeError) as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        if vista.exec():
            self.conf.emit(datos)
            self.close()
        # else no hace nada, deja la tabla abierta para editar


    def leer_datos(self):
        return [[self.mat.item(i, j).text().strip() for j in range(self.n + 1)] for i in range(self.n)] # strip saca el texto a String
            # de la tabla en cada posicion, ij lee el texto

    def random_fill(self): # para llenar la matriz con numeros aleatorios para hacer pruebas rapidas
        for i in range(self.n):
            for j in range(self.n + 1):
                self.mat.item(i,j).setText(str(random.randint(-9, 9)))



class VentanaPasosDetallados(QDialog):
    def __init__(self, pasos_lista, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pasos del método")
        self.resize(800, 750) # tambien falta tamano dinamico

        # Forzar fondo blanco y texto negro en la ventana emergente
        self.setStyleSheet("background-color: white; color: black;")

        scroll = QScrollArea() # porque es vertical y suelen ser muchos pasos
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")

        container = QWidget()
        container.setStyleSheet("background-color: white;")
        layout_container = QVBoxLayout(container)
        layout_container.setSpacing(15) # margen

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        botones = QDialogButtonBox(QDialogButtonBox.Ok)
        botones.accepted.connect(self.accept)
        botones.setStyleSheet("background-color: #f0f0f0; color: black;")
        main_layout.addWidget(botones)


class MetodoDoolittle(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de Doolittle/Crout")
        self.resize(800, 600)

        self.ui = cargar_ui("Doolittle")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (matriz tabla) para que Qt no las cierre
        self.sistema = None # para la matriz confirmada

        # AQUI VAN LOS BOTONES
        self.widget(R_DOOLITTLE).setChecked(True)  # Empieza predeterminado con Gauss
        self.widget(MATRIZ).clicked.connect(self.ingresar_matriz)
        self.widget(MOSTRAR).clicked.connect(self.mostrar_pasos)

        self.widget(BTN_VOLVER).clicked.connect(self.volver.emit) #manda la señal a MenuPrincipal


    def widget(self, nombre):  # busca el nombre del widget en el disenio
        widg = self.ui.findChild(QWidget, nombre)
        if widg is None:
            existentes = [c.objectName() for c in self.ui.findChildren(QWidget)]
            raise LookupError(
                f"No hay un widget llamado '{nombre}'. "
                f"Lista de widgets: {existentes}")
        return widg

    # AQUI van los metodos que dan funcion a cada widget

    def leer_tamano(self):
        try:
            n = int(self.widget(TAMANO).text()) # falta hacer que empiece vacio
            if n >= TAM_MIN and n <= TAM_MAX:
                return n
            else:
                raise ValueError("Ingrese un tamaño válido. "
                                 f"El tamaño del sistema debe de estar entre {TAM_MIN} y {TAM_MAX}")
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None

    def ingresar_matriz(self):
        n = self.leer_tamano()
        if n is None: # no deberia de pasar, ya esta validado
            return

        wind = IngresarnaMatriz(n) # se abre la ventana de tabla del tamano leido
        wind.conf.connect(self.recibir_matriz)
        self.windows.append(wind)
        wind.show()

    def recibir_matriz(self, datos):
        self.sistema = datos_a_matriz(datos) # al confirmar el sistema que es una Matriz de SymPy almacena los datos ingresados como matriz aumentada

    def mostrar_pasos(self):
        if self.sistema is None: # si no hay Matrix
            QMessageBox.warning(self, "Error", "Ingrese un sistema de ecuaciones válido primero.")
            return

        try:
            Lnum, Unum = FactorizacionLU(self.sistema)
            L = Matrix(Lnum)
            U = Matrix(Unum)
            L.simplify()
            U.simplify()
            Llatex = matriz_a_latex(L, False)
            Ulatex = matriz_a_latex(U, False)
            QMessageBox.information(self, "Matrices L y U", f"La matriz L es \n{Llatex}\n La matriz U es \n{Ulatex}",QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Error al generar pasos", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoDoolittle()
    w.show()
    sys.exit(app.exec())
