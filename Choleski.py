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
from sympy import Matrix, preview
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations,
)

CARPETA_UI = Path(__file__).parent # por si en un futuro se mueven directorios
# para otros metodos en Qt Designer los objetnames se cambian solo aqui
TAMANO = "tamEdit"
MATRIZ = "matButton"
BTN_CALCULAR = "calcButton"
MOSTRAR = "pasosButton"
BTN_VOLVER = "unidad4button"

TAM_MIN, TAM_MAX = 2, 10   # tamaños de matriz

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


def AlgoritmoCholeski(M):
    n = M.cols - 1  # cantidad de columnas del sistema - columna b
    A = M[:, :-1]
    L = sp.zeros(n, n)  # inicializa en 0 para ser matriz triangular superior

    for k in range(n):
        suma1 = sum(L[k, s] * L[k, s] for s in range(k))
        valor_raiz = A[k, k] - suma1
        if valor_raiz < 0:
            raise ValueError("La matriz no es definida positiva. No se puede aplicar Choleski.")
        L[k, k] = sp.sqrt(A[k, k] - suma1)

        for i in range(k + 1, n):
            suma2 = sum(L[i, s] * L[k, s] for s in range(k))
            L[i, k] = sp.simplify((A[i, k] - suma2) / L[k, k])

    return L # Regresa matrices de SymPy


def progresiva(M, Vector): # Para Lv = b
    n = M.cols
    sol = sp.zeros(n, 1) # Comienza declarando una matriz (vector)nx1 de SymPy con  ceros
    for i in range(n): # recorre desde 0 hasta n-1
        suma = sum(M[i, j] * sol[j, 0] for j in range(i)) # calcula el producto de los coeficientes de la fila i por las variables que ya fueron resueltas
        sol[i, 0] = (Vector[i, 0] - suma) / M[i, i] # resta terminos conocidos del lado derecho del vector y divide para terminar el despeje
    return sol


def regresiva(M, Vector): # Para Ux = v
    n = M.cols
    sol = sp.zeros(n, 1) # Comienza declarando una matriz (vector)nx1 de SymPy con  ceros
    for i in range(n-1, -1, -1): # desde n-1 hasta 0
        suma = sum(M[i, j] * sol[j, 0] for j in range(i + 1, n)) # suma el producto de los coeficientes ubicados a la derecha de la diagonal por los valores de x que ya se calcularon
        sol[i, 0] = (Vector[i, 0] - suma) / M[i, i]
    return sol


def generar_pasos_detallados(A):
    n = A.rows
    b = A [:, -1] # solo la ultima columna
    L = AlgoritmoCholeski(A)
    pasos_lista = [] # para append

    # Matriz inicial
    latex_A = matriz_a_latex(A, aumentada=True)
    pasos_lista.append({
        "descripcion": "Matriz aumentada inicial del sistema",
        "latex_bloques": [latex_A]
    }) # paso 0

    # luego L y U
    latex_L = matriz_a_latex(L, aumentada=False)
    latex_LT = matriz_a_latex(L.T, aumentada=True)
    bloque_LLT = rf"L = {latex_L} L^T = {latex_LT}"
    pasos_lista.append({
        "descripcion": r"Se calcula la matriz 𝕃 con el algoritmo de Choleski. Tal que A = 𝕃𝕃<sup>T</sup>",  # QLabel renderiza bien texto con unicode
        "latex_bloques": [bloque_LLT]
    })

    # Ecuacion 2 Lv = b
    # se crea v, con variables de Sympy
    v_sym = sp.Matrix([sp.Symbol(f"v_{i+1}") for i in range(n)])
    latex_v = matriz_a_latex(v_sym, False) # usar sp.latex(v_sym) usa corchetes
    latex_b = matriz_a_latex(b, False)
    ecuacion_2 = rf"{latex_L} {latex_v} = {latex_b}" # ecuacion
    pasos_lista.append({
        "descripcion": r"De la ecuación 2, se resuelve el sistema 𝕃<b>v</b> = <b>b</b>", # &#773; es para overline en HTML
        "latex_bloques": [ecuacion_2]
    })

    # progresiva primeto
    v_val = progresiva(L, b)
    latex_v_val = matriz_a_latex(v_val, aumentada=False)
    pasos_lista.append({
        "descripcion": r"Sustitución progresiva para hallar <b>v</b>",
        "latex_bloques": [r"\overline{v} = " + latex_v_val]
    })
    # Ecuacion 1 Ltx = v
    # regresiva despues
    x_sym = sp.Matrix([sp.Symbol(f"x_{i+1}") for i in range(n)])
    latex_x = matriz_a_latex(x_sym, False) # usar sp.latex(x_sym) usa corchetes
    ecuacion_1 = rf"{latex_LT} {latex_x} = {latex_v_val}"
    pasos_lista.append({
        "descripcion": r"Del sistema 𝕃<sup>T</sup><b>x</b> = <b>v</b> se emplea sustitución regresiva para hallar <b>x</b>",
        "latex_bloques": [ecuacion_1]
    })

    # Solución del sistema
    x_val = regresiva(L.T, v_val)
    latex_x_val = matriz_a_latex(x_val, False) # usar sp.latex(x_sym) usa corchetes
    pasos_lista.append({
        "descripcion": r"Con esto se encuentra el vector solución <b>x</b>",
        "latex_bloques": [r"\overline{x} = " + latex_x_val]
    })

    return pasos_lista # regresa el conjunto de pasos como texto en formato LaTeX


class VerMatriz(QDialog):
    def __init__(self, datos, aumentada):
        super().__init__()
        self.setWindowTitle("Confirmar matriz")
        # Forzar fondo blanco y texto negro en la ventana emergente
        self.setStyleSheet("background-color: white; color: black;")

        latex = matriz_a_latex(datos, aumentada)  # ValueError si hay celdas inválidas
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
            vista = VerMatriz(datos, True)
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

            lbl_titulo = QLabel(f"<b>Paso {idx}:</b> {paso.get('descripcion', '')}") # obtiene la descripcion si la hay
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
                line = QLabel("<hr>")
                paso_box.addWidget(line)
                layout_container.addLayout(paso_box)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        botones = QDialogButtonBox(QDialogButtonBox.Ok)
        botones.accepted.connect(self.accept)
        botones.setStyleSheet("background-color: #f0f0f0; color: black;")
        main_layout.addWidget(botones)


class MetodoCholeski(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de Choleski")
        self.resize(800, 600)

        self.ui = cargar_ui("Choleski")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []  # ventanas abiertas (matriz tabla) para que Qt no las cierre
        self.sistema = None # para la matriz confirmada

        # AQUI VAN LOS BOTONES
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
            lista_pasos = generar_pasos_detallados(self.sistema)
            titulo = "Método de Choleski"
            ventana_pasos = VentanaPasosDetallados(lista_pasos, titulo, parent=self)
            self.windows.append(ventana_pasos)
            ventana_pasos.show()
        except Exception as e:
            QMessageBox.warning(self, "Error al generar pasos", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoCholeski()
    w.show()
    sys.exit(app.exec())
