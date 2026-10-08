import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QLineEdit, QTextEdit, QComboBox, \
    QVBoxLayout, QListWidget, QCheckBox, QRadioButton, QSlider, QMessageBox
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader # para Qt Design

# widgets en ambientes de desarrollo de interfaces de usuario graficas (GUI) son los botones, casillas y otros aspectos vizuales interactuables
class MainWindow(QMainWindow): # Clase de la ventana principal

    def __init__(self): # Constructor de la clase
        super().__init__() # Super constructor de la clase

        self.setWindowTitle("Example Window") # Nombre de la ventana

        menubar = self.menuBar() # Para la barra superior

        fileMenu = menubar.addMenu("File")
        editMenu = menubar.addMenu("Edit")
        helpMenu = menubar.addMenu("Help")

        aboutAction = helpMenu.addAction("About") # Sub menus

        submenu = fileMenu.addMenu("Submenu") # Submenu con otro submenu
        exitAction = submenu.addAction("Exit")

        exitAction.triggered.connect(self.close) # Accion para cerrar la ventana (ademas del tache predeterminado de cualquier manejador de ventanas)
        aboutAction.triggered.connect(lambda: print("Info about the program")) # Evento al presionar un menu o submenu

        container = QWidget() # contenedor, es toda la "caja" con los widgets
        self.setCentralWidget(container) # el contenedor es el widget principal, que tiene en si mas widgets

        layout = QVBoxLayout(container) # el layout es una combo box, es decir que se le pueden poner muchas configuraciones en su forma y contenido

        label = QLabel("Label") # Para simples titulos sin interaccion
        label.setAlignment(Qt.AlignCenter) # Se pueden alinear, pero Qt es mejor para disenio que hacerlo manual

        button = QPushButton("Button")  # Boton presionable
        button.clicked.connect(self.do_something) # cuando das click llama una funcion, solo va el nombre de la funcion, sin parentesis ()
        #button.clicled.connect(lambda: print("Button clicked"))

        PopUp = QPushButton("Pop Up") # Boton simple
        PopUp.clicked.connect(self.ask) # llama la funcion ask
        #PopUp.clicked.connect(lambda: QMessageBox.information(self, "Window name", "Info of pop up"))

        buttonW = QPushButton("Open secondary Window") # boton para abrir otra ventana
        buttonW.clicked.connect(self.open_window) # llama la funcion open_window

        line_edit = QLineEdit() # es una simple linea para que el usuario escriba, como para pedir un dato, se puede ajustar el tamanio
        text_edit = QTextEdit() # una caja de texto para que el usuario escriba, se puede ajustar la cantidad de caracteres que caben

        combobox = QComboBox() # el widget que despliega una lista de opciones
        combobox.addItem("1") # tambien se pueden hacer en arreglos o en un for
        combobox.addItem("2")
        combobox.addItem("3")

        listwidget = QListWidget() # widget para listas ya desplegadas
        listwidget.addItem("a") # son tipo tabla
        listwidget.addItem("b")
        listwidget.addItem("c")

        # se puede identificar un click simple o doble click
        listwidget.itemClicked.connect(lambda item: print(f"Item clicked is {item.text()}") )
        listwidget.itemDoubleClicked.connect(lambda item: print(f"Item double clicked is {item.text()}"))

        # lambda es para cuando solo se necesita una accion simple sin necesidad de una funcion completa

        checkbox1 = QCheckBox("One") # cajitas para poner palomitas
        checkbox2 = QCheckBox("Two")
        checkbox3 = QCheckBox("Three")

        inner_container = QWidget() # contenedor interno, como una cajita adentro de una caja
        inner_layout = QVBoxLayout(inner_container)

        radio1 = QRadioButton("x") # tipo opcion multiple
        radio2 = QRadioButton("y")
        radio3 = QRadioButton("z")

        for r in [radio1, radio2, radio3]:
            r.toggled.connect(self.radio_changed)

        inner_layout.addWidget(checkbox1) # se agregarn los checkboxes y radios al layout interno
        inner_layout.addWidget(checkbox2)
        inner_layout.addWidget(checkbox3)

        inner_layout.addWidget(radio1)
        inner_layout.addWidget(radio2)
        inner_layout.addWidget(radio3)

        # slider horizontales y verticales en caso de ser necesarios, en algunos casos si el tamnio de la ventana es muy pequenio algunos sistemas agregan el slider automaticamente
        slider = QSlider() # Horizontal and range
        # slider.setRange(0,100)

        # se agregan todos los witdgets al layout principal
        layout.addWidget(label)
        layout.addWidget(button)
        layout.addWidget(PopUp)
        layout.addWidget(buttonW)
        layout.addWidget(line_edit)
        layout.addWidget(text_edit)
        layout.addWidget(slider)
        layout.addWidget(combobox)
        layout.addWidget(listwidget)

        layout.addWidget(inner_container) # tambien se agrega el layout interno


        self.count = 1 # para contar ventanas externas
        self.windows = [] # arreglo para las ventanas

    def do_something(self):
        print('Button Clicked') # mensaje en terminal

    def radio_changed(self):
        r = self.sender() # segun la opcion elegida
        if(r.isChecked()):
            print('Radio button selected: Value', r.text())

    def ask (self):
        if QMessageBox.question(self, "Question", "Pizza on Pinaple?") == QMessageBox.Yes: # ventana de mensaje, con titulo de la ventana, el mensaje y opciones de botones que presionar
            print('Madman')
        else: # cambia el evento dependiendo del boton
            print('Sane')

    def open_window(self):
        loader = QUiLoader() # llama al loader

        file = QFile("ExampleGUI.ui") # bucsa el archivo, que debe estar en la misma carpeta que el programa
        file.open(QFile.ReadOnly) # lectura del .ui hecho con Qt, dentro de Qt es importante ver los nombres de los widgets para en el codigo principal hacerlos interactivos

        w = loader.load(file) # ventana w es el archivo leido

        #w = SecondaryWindow(self.count)
        self.count += 1 # agrega contador de ventanas
        self.windows.append(w) # agrega la ventana al arreglo

        file.close() # una vez leido, cierra el archivo
        w.show() # muestra la ventana


class SecondaryWindow(QMainWindow): # otra clase para ventana sin formato
    def __init__(self, n):
        super().__init__()
        self.setWindowTitle("Example Window 2")

        label = QLabel(f"Number {n}")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)

app = QApplication()

window = MainWindow() # ventana principal
window.show() # muestra la ventana

app.exec_()