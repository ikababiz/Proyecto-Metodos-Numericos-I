import random
from pathlib import Path
import sys

import io
import shutil
from typing import cast

from PySide6.QtCore import Signal # esta cosa se necesita para mandar una señal para que MenuPrincipal sepa que hacer
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QVBoxLayout, QWidget, QDialog, QLabel, QDialogButtonBox, QTableWidget, QHeaderView,
    QTableWidgetItem, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QPixmap # para imagenes
from PySide6.QtUiTools import QUiLoader
import sympy as sp
from sympy import symbols, Matrix, preview, linsolve
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations,
)

EPSILON = 1e-6  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
# para otros metodos en Qt Designer los objetnames se cambian solo aqui
TAMANO = "tamEdit"
MATRIZ = "matButton"
VECTOR = "vecButton"
MOSTRAR = "pasosButton"
BTN_VOLVER = "unidad5Button"

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


def matriz_a_latex(M): # Modificado ahora sin aumento -------------------------------------------
    # ahora acepta tanto lista de datos como objeto Matrix de SymPy
    if not isinstance(M, Matrix):
        M = datos_a_matriz(M) # Matrix de SymPy

    return sp.latex(M, mat_str="pmatrix", mat_delim=None)


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


def generar_pasos_detallados(A, V0):
    n = A.cols  # cuadrada siempre
    pasos_lista = []

    # Paso 0
    latex_A = matriz_a_latex(A)
    latex_x0 = matriz_a_latex(V0)
    bloque_cero = rf"A = {latex_A} \quad \text{{se propone}} \quad x_0 = {latex_x0}"
    pasos_lista.append({
        "descripcion": "Dada la Matriz 𝔸, se propone el vector inicial <b>x</b><sub>0</sub>.",
        "latex_bloques": [bloque_cero]
    })

    # Comienzan las iteraciones
    error = 1.0
    j = 0
    x_actual = V0
    c_anterior = 0

    while error > EPSILON and j < 200:  # 200 iteraciones maximo

        y = A * x_actual
        c_actual = max(y, key=lambda val: abs(val.evalf())) # para evitar calculo simbolico durante las iteraciones
        x_siguiente = (1 / c_actual) * y

        error = float(abs(c_actual - c_anterior).evalf())

        if j < 2: # Solo las primeras 2 iteraciones se ven en LaTeX

            latex_y = matriz_a_latex(y)
            latex_x_actual = matriz_a_latex(x_actual)
            bloque_y = rf"\text{{Para j = {j}:}} \quad \overline{{y}}^{{({j + 1})}} = A\overline{{x}}^{{({j})}} = {latex_A} {latex_x_actual} = {latex_y}"

            latex_c = sp.latex(c_actual)
            latex_x_siguiente = matriz_a_latex(x_siguiente)
            bloque_x = rf"\overline{{x}}^{{({j + 1})}} = \frac{{1}}{{{latex_c}}} {latex_y} = {latex_x_siguiente}"

            bloque_c = rf"c_{{{j + 1}}} = {latex_c} \quad \text{{(componente dominante de }} \overline{{y}}^{{({j + 1})}} \text{{)}}"

            pasos_lista.append({
                "descripcion": f"Iteración {j+1}: Cálculo del nuevo vector y normalización",
                "latex_bloques": [bloque_y, bloque_c, bloque_x]
            })

        c_anterior = c_actual
        x_actual = x_siguiente
        j += 1

    dots = rf"\vdots"
    pasos_lista.append({
        "descripcion": r"Se continúan iteraciones del algoritmo hasta que converja el vector...",
        "latex_bloques": [dots, dots]
    })

    # Resultados al converger
    x_float = x_actual.applyfunc(lambda val: f"{float(val.evalf()):.4f}") # Se convierte cada elemento de la matriz a float con 4 decimales
    latex_x_actual = matriz_a_latex(x_float)
    bloque_eigenvector = rf"\overline{{x}}^{{({j-1})}} = {latex_x_actual}"
    pasos_lista.append({
        "descripcion": rf"Tras {j} iteraciones, el vector propio dominante aproximado es:",
        "latex_bloques": [bloque_eigenvector]
    })

    # comparacion de eigenvalores numericos vs SymPY
    valores_propios = list(A.eigenvals().keys())
    mayor = max(valores_propios, key=lambda val: abs(val.evalf()))  # para evitar calculo simbolico
    latex_mayor = sp.latex(mayor)
    latex_c_actual = f"{float(c_actual.evalf()):.4f}" # Convertir el escalar a decimal con 4 decimales
    bloque_mayor = rf"\lambda = {latex_c_actual} \approx {latex_mayor}"
    pasos_lista.append({
        "descripcion": r"Finalmente, el mayor valor propio de 𝔸 en valor absoluto es:",
        "latex_bloques": [bloque_mayor]
    })


    return pasos_lista # regresa el conjunto de pasos como texto en formato LaTeX


class VerMatriz(QDialog):
    def __init__(self, datos, parent=None, aumentada=False):
        super().__init__(parent) # no es hija
        self.setWindowTitle("Confirmar")
        # Forzar fondo blanco y texto negro en la ventana emergente
        self.setStyleSheet("background-color: white; color: black;")

        latex = matriz_a_latex(datos)  # ValueError si hay celdas inválidas
        pixmap = latex_a_pixmap(latex)  # RuntimeError si falta LaTeX

        imagen = QLabel() # se mete la imagen en un QLabel
        imagen.setPixmap(pixmap)
        imagen.setAlignment(Qt.AlignCenter) # se muestra centrado
        imagen.setStyleSheet("background-color: white;")

        pregunta = QLabel("¿Los datos ingresados son correctos?")
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

class IngresarMatriz(QWidget): # falta implementar que si ya hay matriz del mismo tamano la despliege
    conf = Signal(list) # emite senal para canfirmar
    def __init__(self,  filas, columnas, titulo="Ingresar Matriz", parent=None):
        super().__init__(parent)
        self.n = filas
        self.n_1 = columnas
        if self.n == self.n_1:
            self.tipo = True  # true es Matriz false es Vector
            self.resize(min(800, 90 * (columnas)), min(600, 50 * (filas + 2)))  # tamano dinamico
        else:
            self.tipo = False
            self.resize(min(800, 300 * (columnas)), min(600, 50 * (filas + 2)))  # tamano dinamico
        self.setWindowTitle(titulo)


        self.mat = QTableWidget(filas, columnas) # matriz de filas x columnas
        if self.tipo:
            self.mat.setHorizontalHeaderLabels([f"a_i{j+1}" for j in range(columnas)]) # nombre de columnas
            self.mat.setVerticalHeaderLabels([f"a_{i + 1}j" for i in range(filas)] ) # nombre de cada fila
        else:
            self.mat.setHorizontalHeaderLabels([f"v_i1"])  # nombre de columnas
            self.mat.setVerticalHeaderLabels([f"v_{i + 1}1" for i in range(filas)])  # nombre de cada fila
        self.mat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(filas):
            for j in range(columnas):
                celda = QTableWidgetItem("") # vacias al inicio
                celda.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.mat.setItem(i, j, celda) # arma la tabla vacia

        if self.tipo:
            self.info = QLabel(f"Introduzca los valores para la matriz A<sub>{filas}&times;{columnas}</sub>")
        else:
            self.info = QLabel(f"Introduzca los valores para el vector inicial V<sub>0</sub>")
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
                    QMessageBox.warning(self, "Faltan datos.", f"La celda a_{i+1}{j+1} está vacía")
                    return

        try: # trata de visualizarla
            vista = VerMatriz(datos, parent=self)
        except (ValueError, RuntimeError) as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        if vista.exec():
            self.conf.emit(datos)
            self.close()
        # else no hace nada, deja la tabla abierta para editar


    def leer_datos(self):
        return [[self.mat.item(i, j).text().strip() for j in range(self.n_1)] for i in range(self.n)] # strip saca el texto a String
            # de la tabla en cada posicion, ij lee el texto

    def random_fill(self): # para llenar la matriz con numeros aleatorios para hacer pruebas rapidas
        for i in range(self.n):
            for j in range(self.n_1):
                self.mat.item(i,j).setText(str(random.randint(-9, 9)))



class VentanaPasosDetallados(QDialog):
    def __init__(self, pasos_lista, titulo,  parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(800, 750)

        # Forzar fondo blanco y texto negro en la ventana emergente
        self.setStyleSheet("background-color: white; color: black;")

        scroll = QScrollArea() # porque es vertical y suelen ser muchos pasos
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")

        container = QWidget()
        container.setStyleSheet("background-color: white;")
        layout_container = QVBoxLayout(container)
        layout_container.setSpacing(15) # margen

        for idx, paso in enumerate(pasos_lista):
            paso_box = QVBoxLayout()

            lbl_titulo = QLabel(f"<b>Fase {idx}:</b> {paso.get('descripcion', '')}") # obtiene la descripcion si la hay
            lbl_titulo.setAlignment(Qt.AlignCenter)
            lbl_titulo.setStyleSheet("color: black; background-color: white;")
            paso_box.addWidget(lbl_titulo)

            for latex_str in paso.get('latex_bloques', []):
                try:
                    pix_latex = latex_a_pixmap(latex_str, dpi=130)
                    lbl_img = QLabel()
                    lbl_img.setPixmap(pix_latex)
                    lbl_img.setAlignment(Qt.AlignCenter)
                    paso_box.addWidget(lbl_img)
                except Exception as e:
                    lbl_err = QLabel(f"Error al renderizar LaTeX: {e}\n{latex_str}")
                    lbl_err.setStyleSheet("color: red; background-color: white;")
                    lbl_err.setAlignment(Qt.AlignCenter)
                    paso_box.addWidget(lbl_err)

                # separador
                #line = QLabel("<hr>")
                #paso_box.addWidget(line)
            layout_container.addLayout(paso_box)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        botones = QDialogButtonBox(QDialogButtonBox.Ok)
        botones.accepted.connect(self.accept)
        botones.setStyleSheet("background-color: #f0f0f0; color: black;")
        main_layout.addWidget(botones)


class MetodoPotencia(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de la Potencia")
        self.resize(800, 600)

        self.ui = cargar_ui("Potencia")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (matriz tabla) para que Qt no las cierre
        self.sistema = None # para la matriz confirmada
        self.vetorInicial = None

        # AQUI VAN LOS BOTONES
        self.widget(MATRIZ).clicked.connect(self.ingresar_matriz)
        self.widget(VECTOR).clicked.connect(self.ingresar_vector)
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

        wind = IngresarMatriz(n, n, titulo="Ingresar la Matriz A") # se abre la ventana de tabla del tamano leido
        wind.conf.connect(self.recibir_matriz)
        self.windows.append(wind)
        wind.show()

    def ingresar_vector(self):
        n = self.leer_tamano()
        if n is None:  # no deberia de pasar, ya esta validado
            return

        windV = IngresarMatriz(n, 1, titulo="Ingresar el Vector Inicial")  # se abre la ventana de tabla del tamano leido
        windV.conf.connect(self.recibir_vector)
        self.windows.append(windV)
        windV.show()

    def recibir_matriz(self, datos):
        self.sistema = datos_a_matriz(datos) # al confirmar que es una Matriz de SymPy almacena los datos ingresados como matriz

    def recibir_vector(self, datos):
        self.vectorInicial = datos_a_matriz(datos)  # al confirmar el vector de SymPy almacena los datos ingresados para v0

    def mostrar_pasos(self):
        if self.sistema is None: # si no hay Matrix
            QMessageBox.warning(self, "Error", "Ingrese una Matriz A primero.")
            return
        if self.vectorInicial is None: # si no hay Matrix
            QMessageBox.warning(self, "Error", "Ingrese un Vector Inicial primero.")
            return
        if self.sistema.cols != self.vectorInicial.rows:
            QMessageBox.warning(self, "Error", "El vector inicial no coincide con el tamaño de la matriz."
                                               "\nRecuerda que las columnas de la matriz deben coincidir exactamente con las filas del vector.")
            return
        try:
            pasos_lista = generar_pasos_detallados(self.sistema, self.vectorInicial)
            # trata de hacer el metodo y cacha la lista de pasos de texto en formato LaTeX
            ventana_pasos = VentanaPasosDetallados(pasos_lista, 'Método de la Potencia', parent=self) # le manda los pasos para que la ventana lo renderice
            self.windows.append(ventana_pasos)
            ventana_pasos.show()
        except Exception as e:
            QMessageBox.warning(self, "Error al generar pasos", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoPotencia()
    w.show()
    sys.exit(app.exec())
