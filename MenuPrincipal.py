import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QLineEdit, QTextEdit, QComboBox, \
    QVBoxLayout, QListWidget, QCheckBox, QRadioButton, QSlider, QMessageBox, QStackedWidget
from PySide6.QtCore import Qt, QFile

from PySide6.QtUiTools import QUiLoader # para Qt Design

from biseccion import MetodoBiseccion # se importa cada clase de cada metodo
from Gauss import MetodoGauss

CARPETA_UI = Path(__file__).parent # carpeta donde están los .ui (la misma que este archivo)
# si se cambian las direcciones de archivos hay que cambiar la ruta
def cargar_ui(nombre):
    file = QFile(str(CARPETA_UI / f"{nombre}.ui"))
    if not file.open(QFile.ReadOnly):
        raise FileNotFoundError(f"No se encontró {nombre}.ui en {CARPETA_UI}")
    w = QUiLoader().load(file)
    file.close()
    return w # se lee y carga cada disenio


class MainWindow(QMainWindow):
    def __init__(self): # Constructor de la clase
        super().__init__() # Super constructor de la clase
        self.setWindowTitle("Métodos Numéricos I")
        self.resize(800, 600) # tamaño predeterminado creo que es portrait
        self.pila = QStackedWidget()
        self.setCentralWidget(self.pila)

        self.paginas = {} # se cargan todos los diseños y se agregan como widgets
        for nombre in ["Introduccion", "Unidades", "Unidad2", "Unidad3", "Unidad4", "Unidad5"]: # aqui se modifica si se agregan mas disenios
            self.agregar_pagina(nombre, cargar_ui(nombre)) # cada diseño se carga y se agrega a la pila

        # cada metodo tiene su propia clase
        bis = MetodoBiseccion()
        self.agregar_pagina("Biseccion", bis)

        gauss = MetodoGauss()
        self.agregar_pagina("Gauss", gauss)

        # navegación: (página donde está el botón, nombre del botón, página destino)
        # el nombre del botón es su objectName en Qt Designer
        self.conectar("Introduccion", "menubutton", "Unidades")
        self.conectar("Unidades", "unidad2button", "Unidad2")
        self.conectar("Unidades", "unidad3button", "Unidad3")
        self.conectar("Unidades", "unidad4button", "Unidad4")
        self.conectar("Unidades", "unidad5button", "Unidad5")
        self.conectar("Unidades", "backbutton", "Introduccion")

        # Unidad 2
        self.conectar("Unidad2", "menubutton", "Unidades")
        bis.volver.connect(lambda: self.ir_a("Unidad2")) # cuando se manda la señal
        self.conectar("Unidad2", "biseccionbutton", "Biseccion")
        self.conectar("Biseccion", "unidad2button", "Unidad2")

        # Unidad 3
        self.conectar("Unidad3", "menubutton", "Unidades")
        gauss.volver.connect(lambda: self.ir_a("Unidad3"))
        self.conectar("Unidad3", "gaussbutton", "Gauss")
        self.conectar("Gauss", "unidad3button", "Unidad3")

        self.conectar("Unidad4", "menubutton", "Unidades")
        self.conectar("Unidad5", "menubutton", "Unidades")

        self.ir_a("Introduccion") # Empieza de predeterminado en la intro


    def agregar_pagina(self, nombre, pagina):
        self.pila.addWidget(pagina)
        self.paginas[nombre] = pagina

    def conectar(self, pagina, nombre_boton, destino):
        boton = self.paginas[pagina].findChild(QPushButton, nombre_boton)
        if boton is None:
            QMessageBox.warning(
                self, "Botón no encontrado",f"En {pagina}.ui no hay un botón llamado '{nombre_boton}'.")
            return
        # lambda con valor por defecto para que cada botón recuerde su destino
        boton.clicked.connect(lambda checked=False, d=destino: self.ir_a(d))

    def ir_a(self, nombre):
        self.pila.setCurrentWidget(self.paginas[nombre])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
