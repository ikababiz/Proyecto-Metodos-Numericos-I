import random
from pathlib import Path
import sys
import io
import shutil
import numpy as np
import sympy as sp

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QVBoxLayout, QWidget, QDialog, QLabel,
    QDialogButtonBox, QTableWidget, QHeaderView, QTableWidgetItem,
    QPushButton, QHBoxLayout, QScrollArea
)
from PySide6.QtCore import Qt, QFile
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
import sympy as sp
from sympy import symbols, Matrix, preview, linsolve
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations,
)
from Tabla_resultados import VentanaTabla

EPSILON = 1e-6  # valor muy pequeño > 0
MAX_ITER = 100

CARPETA_UI = Path(__file__).parent

# ObjectNames definidos en Qt Designer
R_JACOBI = "jacobiRadio"
R_GAUSS_SEIDEL = "gaussSeidelRadio"
TAMANO = "tamEdit"
MATRIZ = "matButton"
BTN_CALCULAR = "calcButton"
TABLA = "tablaButton"
BTN_VOLVER = "unidad3button"

TAM_MIN, TAM_MAX = 2, 10  # Tamaños de matriz permitidos

TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application, convert_xor,
)


def cargar_ui(nombre):
    file = QFile(str(CARPETA_UI / f"{nombre}.ui"))
    if not file.open(QFile.ReadOnly):
        raise FileNotFoundError(f"No se encontró {nombre}.ui en {CARPETA_UI}")
    widget = QUiLoader().load(file)
    file.close()
    return widget


def datos_a_matriz(datos):
    try:
        return Matrix([[parse_expr(c, transformations=TRANSFORMACIONES) for c in fila] for fila in datos])
    except Exception as e:
        raise ValueError(f"No se pudo interpretar la matriz: {e}")


def matriz_a_latex(M, aumentada=True):
    """Devuelve el LaTeX de la matriz (acepta tanto lista de datos como objeto Matrix de SymPy)."""
    if not isinstance(M, Matrix):
        M = datos_a_matriz(M)
    if not aumentada:
        return sp.latex(M, mat_str="pmatrix", mat_delim=None)
    n = M.cols - 1
    cuerpo = r" \\ ".join(
        " & ".join(sp.latex(M[i, j]) for j in range(M.cols))
        for i in range(M.rows))
    return (r"\left(\begin{array}{" + "c" * n + "|c}" + cuerpo + r"\end{array}\right)")


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



def latex_a_pixmap(latex, dpi=150):
    """Compila el LaTeX con sympy.preview y devuelve un QPixmap."""
    if shutil.which("latex") is None or shutil.which("dvipng") is None:
        raise RuntimeError("Falta LaTeX en esta computadora (comandos 'latex' y 'dvipng').")
    buffer = io.BytesIO()
    preview(f"$\\displaystyle {latex}$", output="png", viewer="BytesIO",
            outputbuffer=buffer, euler=False, dvioptions=["-D", str(dpi)])
    pixmap = QPixmap()
    pixmap.loadFromData(buffer.getvalue())
    return pixmap


def generar_encabezado(n):
    return ["n"] + [f"x_{i + 1}" for i in range(n)]


def diagonal_dominante(matriz, vector):
    rows    = np.size(matriz, 0)
    columns = np.size(matriz, 1)

    vector_permutado = np.arange(rows)
    matriz_permutada = np.identity(rows)

    if rows != columns:
        return matriz, vector, matriz_permutada, vector_permutado, vector_permutado, False

    valores_abs  = np.zeros(rows)
    matriz_copia = np.copy(matriz)
    vector_copia = np.copy(vector)
    vector_permutado_copia = np.copy(vector_permutado)
    vector_permutado_x = np.copy(vector_permutado)
    vector_permutado_x_copia = np.copy(vector_permutado_x)

    matriz_permutada_copia = np.copy(matriz_permutada)

    for i in range(0, rows):
        aux = abs(matriz_copia.diagonal()[i])
        valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - aux

        if aux <= valores_abs[i]:
            aux_k, aux_l = i, i
            for k in range(i, rows):
                for l in range(i, columns):
                    aux_dos = abs(matriz_copia[k, l])
                    if aux < aux_dos:
                        aux = aux_dos
                        aux_k, aux_l = k, l

            matriz_copia[:,[i, aux_l]] = matriz_copia[:,[aux_l, i]]
            matriz_copia[[i, aux_k]]   = matriz_copia[[aux_k, i]]

            matriz_permutada_copia[:,[i, aux_l]] = matriz_permutada_copia[:,[aux_l, i]]
            matriz_permutada_copia[[i, aux_k]]   = matriz_permutada_copia[[aux_k, i]]

            vector_copia[i], vector_copia[aux_k] = vector_copia[aux_k], vector_copia[i]

            vector_permutado_copia[i], vector_permutado_copia[aux_k] = vector_permutado_copia[aux_k], vector_permutado_copia[i]
            vector_permutado_x_copia[i], vector_permutado_x_copia[aux_l] = vector_permutado_x_copia[aux_l], vector_permutado_x_copia[i]

            valores_abs[i] = np.sum(np.absolute(matriz_copia[i,:])) - abs(matriz_copia.diagonal()[i])

    for i in range(0, rows):
        if valores_abs[i] >= abs(matriz_copia.diagonal()[i]):
            return matriz, vector, matriz_permutada, vector_permutado, vector_permutado_x, False

    return matriz_copia, vector_copia, matriz_permutada_copia, vector_permutado_copia, vector_permutado_x_copia, True

def despejar_variables(matriz, vector_b, vector_n, px):
    rows = np.size(matriz, 0)
    columns = np.size(matriz, 1)
    diagonal = {}
    ecuaciones = [""] * rows
    despejados = [None] * rows

    for i in range(rows):
        ecuaciones[i] += "("+str(vector_b[i])
        for j in range(columns):
            if i != j: ecuaciones[i] += " - "+str(matriz[i, j])+"*x_"+str(px[j])
        ecuaciones[i] += ")/"+str(matriz[i, i])
        despejados[i] = sp.parse_expr(ecuaciones[i])
        diagonal["x_"+str(i)] = vector_n[i]

    return despejados, diagonal


def calcular_jacobi(matriz, vector_b, vector_n, diagonal, px, despejados):
    dominante = True
    matriz, vector_b, _, pb, px, dominante = diagonal_dominante(matriz, vector_b)

    if not dominante:
        raise ValueError("La matriz no se puede reordenar para que sea estrictamente diagonal dominante.")

    despejados, diagonal = despejar_variables(matriz, vector_b, vector_n, px)

    rows = np.size(matriz, 0)
    columns = np.size(matriz, 1)
    vector_n1 = np.zeros(rows)
    vector_diff = np.zeros(rows)
    parar = [False] * rows
    filas = []

    i = 0
    vector_n = vector_n[px]
    while i < MAX_ITER and not all(parar):
        for j in range(rows):
            vector_n1[j] = despejados[j].evalf(subs=diagonal)
            vector_diff[j] = abs(vector_n1[j] - vector_n[j])
            parar[j] = EPSILON > vector_diff[j]

        vector_n = np.copy(vector_n1)
        diagonal = {"x_"+str(px[j]): vector_n1[j] for j in range(rows)}

        filas.append([i] + [float(diagonal['x_'+str(j)]) for j in range(rows)])
        
        i += 1

    if i == MAX_ITER and not all(parar): print("Se agotaron las iteraciones.")

    return filas


class VerMatriz(QDialog):
    def __init__(self, datos, parent=None, aumentada=True):
        super().__init__(parent)
        self.setWindowTitle("Confirmar matriz")

        latex = matriz_a_latex(datos, aumentada)
        pixmap = latex_a_pixmap(latex)

        imagen = QLabel()
        imagen.setPixmap(pixmap)
        imagen.setAlignment(Qt.AlignCenter)

        pregunta = QLabel("¿La matriz ingresada es correcta?")
        pregunta.setAlignment(Qt.AlignCenter)

        botones = QDialogButtonBox()
        botones.addButton("Sí, continuar", QDialogButtonBox.AcceptRole)
        botones.addButton("No, hacer cambios", QDialogButtonBox.RejectRole)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(imagen)
        layout.addWidget(pregunta)
        layout.addWidget(botones)


class IngresarnaMatriz(QWidget):
    conf = Signal(list)

    def __init__(self, n):
        super().__init__()
        self.n = n
        self.setWindowTitle("Ingresar Sistema de Ecuaciones")
        self.resize(min(800, 90 * (n)), min(600, 50 * (n + 2)))

        self.mat = QTableWidget(n, n + 1)
        self.mat.setHorizontalHeaderLabels([f"x_{j + 1}" for j in range(n)] + ["b"])
        self.mat.setVerticalHeaderLabels([f"Ec. {i + 1}" for i in range(n)])
        self.mat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(n):
            for j in range(n + 1):
                celda = QTableWidgetItem("")
                celda.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.mat.setItem(i, j, celda)

        self.info = QLabel(f"Llene la matriz de coeficientes {n}x{n} y la columna b de términos independientes")
        self.info.setWordWrap(True)

        confButton = QPushButton("Confirmar")
        confButton.clicked.connect(self.confirmar)
        randButton = QPushButton("RandomFill")
        randButton.clicked.connect(self.random_fill)

        layout = QVBoxLayout(self)
        layout.addWidget(self.mat)
        layout.addWidget(self.info)
        layout.addWidget(randButton)
        layout.addWidget(confButton)

    def confirmar(self):
        datos = self.leer_datos()
        for i, fila in enumerate(datos):
            for j, texto in enumerate(fila):
                if texto == "":
                    self.mat.setCurrentCell(i, j)
                    QMessageBox.warning(self, "Sistema incompleto", f"La celda a_{i + 1}{j + 1} está vacía")
                    return

        try:
            vista = VerMatriz(datos, parent=self, aumentada=True)
        except (ValueError, RuntimeError) as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        if vista.exec():
            self.conf.emit(datos)
            self.close()

    def leer_datos(self):
        return [[self.mat.item(i, j).text().strip() for j in range(self.n + 1)] for i in range(self.n)]

    def random_fill(self):
        for i in range(self.n):
            for j in range(self.n + 1):
                self.mat.item(i, j).setText(str(random.randint(-9, 9)))

class MetodoJacobi(QWidget):
    volver = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Método de Jacobi/Gauss-Seidel")
        self.resize(800, 600)

        self.ui = cargar_ui("Jacobi")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.windows = []
        self.sistema = None

        # Configuración inicial por defecto
        self.widget(R_JACOBI).setChecked(True)

        # Conexiones de botones
        self.widget(MATRIZ).clicked.connect(self.ingresar_matriz)
        self.widget(BTN_CALCULAR).clicked.connect(self.calcular_solucion)
        self.widget(TABLA).clicked.connect(self.tabla)
        self.widget(BTN_VOLVER).clicked.connect(self.volver.emit)

    def widget(self, nombre):
        widg = self.ui.findChild(QWidget, nombre)
        if widg is None:
            existentes = [c.objectName() for c in self.ui.findChildren(QWidget)]
            raise LookupError(f"No hay un widget llamado '{nombre}'. Widgets existentes: {existentes}")
        return widg

    def leer_tamano(self):
        try:
            n = int(self.widget(TAMANO).text())
            if TAM_MIN <= n <= TAM_MAX:
                return n
            else:
                raise ValueError(f"Ingrese un tamaño válido entre {TAM_MIN} y {TAM_MAX}.")
        except ValueError as e:
            QMessageBox.warning(self, "Datos inválidos", str(e))
            return None

    def leer_filas(self):
        if self.sistema is None: # Si no hay sistema ingresado
            QMessageBox.warning(self, "Error", "Ingrese un sistema de ecuaciones válido primero.")
            return None
        try:
            self.jacob = self.widget(R_JACOBI).isChecked() # detecta el metodo elegido por el usuario
            A = np.array(self.sistema[:, :-1].tolist(), dtype=float)
            b = np.array(self.sistema[:, -1].tolist(), dtype=float).flatten()
            return calcular_jacobi(A, b, np.ones(A.shape[0])) # envia el sistema y el metodo
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e)) # error generico
            return None

    def ingresar_matriz(self):
        n = self.leer_tamano()
        if n is None:
            return

        wind = IngresarnaMatriz(n)
        wind.conf.connect(self.recibir_matriz)
        self.windows.append(wind)
        wind.show()

    def recibir_matriz(self, datos):
        self.sistema = datos_a_matriz(datos)

    def calcular_solucion(self): # Funciona con sp.solve pero seria ideal que llame calcular_jacobi y de la ultima iteracion muestre el resultado al que convergen
        if self.sistema is None:
            QMessageBox.warning(self, "Error", "Ingrese un sistema de ecuaciones válido primero.")
            return

        latex, nota = solucion_a_latex(self.sistema)
        if latex is None:
            QMessageBox.information(self, "Solución", nota)
            return
        try:
            QDialog()  # placeholder
            from PySide6.QtWidgets import QDialogButtonBox
            class VentanaLaTeX(QDialog):
                def __init__(self, titulo, latex, nota="", parent=None):
                    super().__init__(parent)
                    self.setWindowTitle(titulo)
                    imagen = QLabel()
                    imagen.setPixmap(latex_a_pixmap(latex))
                    imagen.setAlignment(Qt.AlignCenter)
                    layout = QVBoxLayout(self)
                    layout.addWidget(imagen)
                    if nota:
                        etiqueta = QLabel(nota)
                        etiqueta.setAlignment(Qt.AlignCenter)
                        layout.addWidget(etiqueta)
                    botones = QDialogButtonBox(QDialogButtonBox.Ok)
                    botones.accepted.connect(self.accept)
                    layout.addWidget(botones)

            VentanaLaTeX("Solución del sistema", latex, nota, parent=self).exec()
        except RuntimeError as e:
            QMessageBox.information(self, "Solución", f"{nota}\n\n{latex}")

    def tabla(self):
        filas = self.leer_filas()
        if not filas:
            return
        n = int(self.widget(TAMANO).text())
        encabezado = generar_encabezado(n)
        nombre = "Jacobi" if self.widget(R_JACOBI).isChecked() else "Gauss-Seidel"
        w2 = VentanaTabla(f"Método de {nombre}", encabezado, filas)
        self.windows.append(w2)
        w2.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoJacobi()
    w.show()
    sys.exit(app.exec())
