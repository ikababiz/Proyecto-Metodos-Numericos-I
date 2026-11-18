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
VECTOR = "vecButton"
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


def matriz_a_latex(M, aumentada):
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

    if rows != columns: # creo que esto nunca pasa por previas validaciones
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


def calcular_jacobi(matriz, vector_b, vector_n, jacob):
    dominante = True
    matriz, vector_b, _, pb, px, dominante = diagonal_dominante(matriz, vector_b)

    if jacob and not dominante:
        raise ValueError("La matriz no se puede reordenar para que sea diagonal dominante.")
    elif not dominante:
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
            if not jacob: diagonal = {"x_"+str(px[j]): vector_n1[j] for j in range(rows)}

        vector_n = np.copy(vector_n1)
        if jacob: diagonal = {"x_"+str(px[j]): vector_n1[j] for j in range(rows)}

        filas.append([i] + [float(diagonal['x_'+str(j)]) for j in range(rows)])
        
        i += 1


    return filas


class VerMatriz(QDialog):
    def __init__(self, datos, parent=None, aumentada=True):
        super().__init__(parent)
        self.setWindowTitle("Confirmar")

        latex = matriz_a_latex(datos, aumentada)
        pixmap = latex_a_pixmap(latex)

        imagen = QLabel()
        imagen.setPixmap(pixmap)
        imagen.setAlignment(Qt.AlignCenter)

        pregunta = QLabel("¿Los datos ingresados son correctos?")
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


class IngresarMatriz(QWidget): # falta implementar que si ya hay matriz del mismo tamano la despliege
    conf = Signal(list) # emite senal para canfirmar
    def __init__(self,  filas, columnas, titulo="Ingresar Matriz", parent=None):
        super().__init__(parent)
        self.n = filas
        self.n_1 = columnas
        if columnas != 1:
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
            if self.n_1 != 1:
                vista = VerMatriz(datos, parent=self, aumentada=True)
            else:
                vista = VerMatriz(datos, parent=self, aumentada=False)
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
        self.vectorInicial = None

        # Configuración inicial por defecto
        self.widget(R_JACOBI).setChecked(True)

        # Conexiones de botones
        self.widget(MATRIZ).clicked.connect(self.ingresar_matriz)
        self.widget(VECTOR).clicked.connect(self.ingresar_vector)
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
        if self.vectorInicial is None:  # si no hay Matrix
            QMessageBox.warning(self, "Error", "Ingrese un Vector Inicial primero.")
            return
        if self.sistema.cols-1 != self.vectorInicial.rows:
            QMessageBox.warning(self, "Error", "El vector inicial no coincide con el tamaño de la matriz."
                                               "\nRecuerda que las columnas de la matriz deben coincidir exactamente con las filas del vector.")
            return
        try:
            self.jacob = self.widget(R_JACOBI).isChecked() # detecta el metodo elegido por el usuario
            A = np.array(self.sistema[:, :-1].tolist(), dtype=float)
            b = np.array(self.sistema[:, -1].tolist(), dtype=float).flatten()
            vector_n = np.array(self.vectorInicial.tolist(), dtype=float).flatten()
            return calcular_jacobi(A, b, vector_n, self.jacob) # envia el sistema y el metodo
        except ValueError as e:
            QMessageBox.warning(self, "Error: ", str(e)) # error generico
            return None

    def ingresar_matriz(self):
        n = self.leer_tamano()
        if n is None:
            return

        wind = IngresarMatriz(n, n+1, titulo="Ingresar la Matriz A")
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
        self.sistema = datos_a_matriz(datos)

    def recibir_vector(self, datos):
        self.vectorInicial = datos_a_matriz(datos)  # al confirmar el vector de SymPy almacena los datos ingresados para v0

    def calcular_solucion(self): # Funciona con sp.solve pero seria ideal que llame calcular_jacobi y de la ultima iteracion muestre el resultado al que convergen
        filas = self.leer_filas()
        if not filas:
            return

        i_final = filas[-1][0] # la ultima iteracion
        solucion = filas[-1][1:] # toda le fila excepto la primer columna (i)

        # lates = solucion_a_latex(ctm)
        # se arma la solucion en latex
        vec_sol = r" \\ ".join([f"{v:.4f}" for v in solucion])
        latex = rf"\overline{{x}} \approx \begin{{pmatrix}} {vec_sol} \end{{pmatrix}}"
        if self.widget(R_JACOBI).isChecked():
            nombre = "Jacobi"
        else:
            nombre = "Gauss-Seidel"
        if i_final >= MAX_ITER-1:
            nota = f"El método de {nombre} se detuvo tras {i_final} iteraciones sin converger bajo la tolerancia esperada.\n"
        else:
            nota = f"Convergencia alcanzada con el metodo de {nombre} tras {i_final} iteraciones."

        try:
            VentanaLaTeX("Solución aproximada del sistema", latex, nota = nota, parent=self).exec()
        except RuntimeError as e:
            QMessageBox.information(self, "Solución en texto plano.", f"{nota}\n{latex}") # Si la ventana falla, sale en texto plano


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
