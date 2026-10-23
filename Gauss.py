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
from sympy import symbols, Matrix, preview, linsolve
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations,
)

EPSILON = 1e-6  # valor muy pequeño > 0

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
# para otros metodos en Qt Designer los objetnames se cambian solo aqui
R_GAUSS = "gaussRadio"
R_GAUSS_JORDAN = "gaussjordanRadio"
PARCIAL_BOX = "parcialBox"
TOTAL_BOX = "totalBox"
TAMANO = "tamEdit"
MATRIZ = "matButton"
BTN_CALCULAR = "calcButton"
MOSTRAR = "pasosButton"
BTN_VOLVER = "unidad3button"

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

def solucion_a_latex(M):
    xs = symbols(f"x_1:{M.cols}") # se declaran x_n symbols, dependiendo del tamanio de n seran x_1,...,x_n
    sol = sp.linsolve((M[:, :-1], M[:, -1]), *xs) # de la matrix linsolve devuelve los valores de resultados en los symbols declarados

    if sol == sp.EmptySet:
        return None, "El sistema no tiene solución." #incompatible indeterminable

    valores = list(sol)[0]
    libres = [x for x in xs if any(v.has(x) for v in valores)]

    vector = (r"\begin{pmatrix}"
              + r" \\ ".join(sp.latex(v) for v in valores)
              + r"\end{pmatrix}") # se hace el vector solucion
    latex = r"\overline{x} = " + vector
    if libres: # solo si el sistema tiene infinitas soluciones
        latex += r",\quad " + ", ".join(sp.latex(x) for x in libres) + r" \in \mathbb{R}"
        nombres = ", ".join(str(x) for x in libres)
        nota = f"El sistema tiene soluciones infinitas. Variables libres: {nombres}."
    else:
        nota = "Solución única."
    return latex, nota # devuelve la cadena y la nota dependiendo del caso de solucion


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

def generar_pasos_detallados(M_orig, gauss_jordan=False, pivoteo_parcial=False):
    """Genera la lista de pasos (matriz, operacion, matriz_resultante)."""
    M = M_orig.copy() # copia para no perderla
    filas, cols = M.shape
    pasos_lista = [] # para append

    # Matriz inicial
    pasos_lista.append({
        "matriz": M.copy(),
        "operacion": r"\text{Matriz aumentada inicial del sistema}"
    }) # paso 0

    for i in range(min(filas, cols - 1)):
        # checa si pivoteo parcial está activo
        if pivoteo_parcial:
            max_val = abs(M[i, i]) # mayor
            max_row = i # localizacion
            for k in range(i + 1, filas):
                if abs(M[k, i]) > max_val:
                    max_val = abs(M[k, i])
                    max_row = k
            if max_row != i:  # si no coinciden se cambiab
                M.row_swap(i, max_row)
                pasos_lista.append({
                    "matriz": M.copy(), # instruccion
                    "operacion": f"R_{{{i + 1}}} \\leftrightarrow R_{{{max_row + 1}}} \\quad \\text{{(Pivoteo parcial)}}"
                })

        # Verificar pivote es casi cero
        if abs(M[i, i]) < EPSILON:
            continue

        # Hacer pivote 1, opcional en ambos metodos creo
        pivote = M[i, i]
        if pivote != 1:
            inv_pivote = sp.Rational(1, pivote) if isinstance(pivote, (int, sp.Integer, sp.Rational)) else 1 / pivote
            M[i, :] = M[i, :] / pivote
            pasos_lista.append({
                "matriz": M.copy(),
                "operacion": f"({sp.latex(inv_pivote)}) R_{{{i + 1}}} \\rightarrow R_{{{i + 1}}}^*"
            })

        # Eliminar elementos debajo del pivote
        for j in range(i + 1, filas):
            factor = M[j, i]
            if factor != 0:
                M[j, :] = M[j, :] - factor * M[i, :]
                inv_factor = -factor
                signo = "+" if inv_factor > 0 else ""
                pasos_lista.append({
                    "matriz": M.copy(),
                    "operacion": f"{signo}{sp.latex(inv_factor)} R_{{{i + 1}}} + R_{{{j + 1}}} \\rightarrow R_{{{j + 1}}}^*"
                })

    # Si es Gauss-Jordan, limpiar también arriba de los pivotes para evitar sustitucion regresiva
    if gauss_jordan:
        for i in range(min(filas, cols - 1) - 1, -1, -1):
            if abs(M[i, i]) < EPSILON:
                continue
            for j in range(i - 1, -1, -1):
                factor = M[j, i]
                if factor != 0:
                    M[j, :] = M[j, :] - factor * M[i, :]
                    inv_factor = -factor
                    signo = "+" if inv_factor > 0 else ""
                    pasos_lista.append({
                        "matriz": M.copy(),
                        "operacion": f"{signo}{sp.latex(inv_factor)} R_{{{i + 1}}} + R_{{{j + 1}}} \\rightarrow R_{{{j + 1}}}^*"
                    })

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


class VentanaLaTeX(QDialog):
    def __init__(self, titulo, latex, nota="", parent=None):
        super().__init__(parent) # huerfana
        self.setWindowTitle(titulo)
        # Forzar fondo blanco y texto negro en la ventana emergente
        self.setStyleSheet("background-color: white; color: black;")

        imagen = QLabel() # le llega la cadena el LaTeX y la pasa a imagen
        imagen.setPixmap(latex_a_pixmap(latex))
        imagen.setAlignment(Qt.AlignCenter)
        imagen.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(self)
        layout.addWidget(imagen)
        if nota: # si se manda nota se crea un Qlabel
            etiqueta = QLabel(nota)
            etiqueta.setAlignment(Qt.AlignCenter)
            etiqueta.setStyleSheet("color: black; background-color: white;")
            layout.addWidget(etiqueta)

        botones = QDialogButtonBox(QDialogButtonBox.Ok) # okay
        botones.accepted.connect(self.accept) # cierra al dar ok
        botones.setStyleSheet("background-color: #f0f0f0; color: black;")
        layout.addWidget(botones)


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

        for idx, paso in enumerate(pasos_lista):
            paso_box = QVBoxLayout()

            lbl_titulo = QLabel(f"<b>Paso {idx}:</b>")
            lbl_titulo.setAlignment(Qt.AlignCenter)
            lbl_titulo.setStyleSheet("color: black; background-color: white;")
            paso_box.addWidget(lbl_titulo)

            try:
                pix_op = latex_a_pixmap(paso['operacion'], dpi=130)
                lbl_op_img = QLabel()
                lbl_op_img.setPixmap(pix_op)
                lbl_op_img.setAlignment(Qt.AlignCenter)
                lbl_op_img.setStyleSheet("background-color: white;")
                paso_box.addWidget(lbl_op_img)
            except Exception:
                lbl_op_fallback = QLabel(paso['operacion'])
                lbl_op_fallback.setAlignment(Qt.AlignCenter)
                lbl_op_fallback.setStyleSheet("color: black; background-color: white;")
                paso_box.addWidget(lbl_op_fallback)

            try:
                latex_mat = matriz_a_latex(paso['matriz'], aumentada=True)
                pix_mat = latex_a_pixmap(latex_mat, dpi=140)
                lbl_mat_img = QLabel()
                lbl_mat_img.setPixmap(pix_mat)
                lbl_mat_img.setAlignment(Qt.AlignCenter)
                lbl_mat_img.setStyleSheet("background-color: white;")
                paso_box.addWidget(lbl_mat_img)
            except Exception as e:
                lbl_err = QLabel(f"[Error al renderizar matriz: {e}]")
                lbl_err.setStyleSheet("color: red; background-color: white;")
                paso_box.addWidget(lbl_err)

            layout_container.addLayout(paso_box)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        botones = QDialogButtonBox(QDialogButtonBox.Ok)
        botones.accepted.connect(self.accept)
        botones.setStyleSheet("background-color: #f0f0f0; color: black;")
        main_layout.addWidget(botones)


class MetodoGauss(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de Gauss/Gauss-Jordan")
        self.resize(800, 600)

        self.ui = cargar_ui("Gauss")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (matriz tabla) para que Qt no las cierre
        self.sistema = None # para la matriz confirmada

        # AQUI VAN LOS BOTONES
        self.widget(R_GAUSS).setChecked(True)  # Empieza predeterminado con Gauss
        self.widget(PARCIAL_BOX).setChecked(True)  # Empieza predeterminado con Pivote Parcial
        self.widget(MATRIZ).clicked.connect(self.ingresar_matriz)
        self.widget(BTN_CALCULAR).clicked.connect(self.calcular_solucion)
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

    def calcular_solucion(self):
        if self.sistema is None:
            QMessageBox.warning(self, "Error", "Ingrese un sistema de ecuaciones válido primero.")
            return

        latex, nota = solucion_a_latex(self.sistema)
        if latex is None:
            QMessageBox.information(self, "Solucíón.", nota)
            return
        try:
            VentanaLaTeX("Solución del sistema", latex, nota, parent=self).exec()
        except RuntimeError as e:
            QMessageBox.information(self, "Solución", f"{nota}\n\n{latex}")

    def mostrar_pasos(self):
        if self.sistema is None: # si no hay Matrix
            QMessageBox.warning(self, "Error", "Ingrese un sistema de ecuaciones válido primero.")
            return

        # Leer estado actual de los RadioButtons y CheckBoxes al momento de presionar el botón
        metodo_gj = self.widget(R_GAUSS_JORDAN).isChecked()
        pivoteo_parcial = self.widget(PARCIAL_BOX).isChecked()

        try:
            pasos_lista = generar_pasos_detallados(self.sistema, gauss_jordan=metodo_gj,
                                                   pivoteo_parcial=pivoteo_parcial)
            # trata de hacer el metodo y cacha la lista de pasos de texto en formato LaTeX
            ventana_pasos = VentanaPasosDetallados(pasos_lista, parent=self) # le manda los pasos para que la ventana lo renderice
            self.windows.append(ventana_pasos)
            ventana_pasos.show()
        except Exception as e:
            QMessageBox.warning(self, "Error al generar pasos", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoGauss()
    w.show()
    sys.exit(app.exec())
