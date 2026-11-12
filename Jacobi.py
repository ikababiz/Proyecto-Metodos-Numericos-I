import random
from pathlib import Path
import sys
import io
import shutil

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


def diagonal_dominante(M, jacob): # falta intentar cambiar renglones
    n = M.cols - 1
    if jacob:
        return all(abs(M[i, i]) >= sum(abs(M[i, j]) for j in range(n) if j != i) # valor absoluto pivote mayor o igual a la suma del resto
               for i in range(n)) # all evalua si se cumple la condicion para todos los for, regresa true o false
    else:
        return all(abs(M[i, i]) > sum(abs(M[i, j]) for j in range(n) if j != i) # valor absoluto pivote mayor a la suma del resto
               for i in range(n)) # all evalua si se cumple la condicion para todos los for, regresa true o false

def despejar_variables(M):
    n = M.rows
    vars = symbols(f"x_1:{n + 1}")
    # Falta hacer despejes  <-------------------------------------
    despejes = ['x_1 = 5x_2 + x_3', 'x_2 = ...'] # ejemplo

    return despejes # ? imagino que deberia de retornar un arreglo con cada despeje


def calcular_jacobi(M, jacob):
    diag = diagonal_dominante(M, jacob)
    if diag:
        max_iter = 200
        filas = []
        n = 1
        # sigue el bucle while
        # despejar cada variable con despejar_variables <---------------------------
        despejes = despejar_variables(M)
        # evaluar cada variable dependiendo del metodo
        if jacob:
            # formulas Jacobi
            filas.append(n) # n, x_1, x_2, ...
            print()
        else:
            # formulas Gauss-Seidel
            filas.append(n)  # n, x_1, x_2, ...
            print()
        #n += 1
    else:
        print("El sistema no cumple con los requisitos") # esto deberia de ser un Warning




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
            self.jacob = self.widget(R_JACOBI).ischecked() # detecta el metodo elegido por el usuario
            return calcular_jacobi(self.sistema, self.jacob) # envia el sistema y el metodo
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
        encabezado = self.generar_encabezado(n)
        nombre = "Jacobi" if self.widget(R_JACOBI).isChecked() else "Gauss-Seidel"
        w2 = VentanaTabla(f"Método de {nombre}", encabezado, filas)
        self.windows.append(w2)
        w2.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MetodoJacobi()
    w.show()
    sys.exit(app.exec())