from PySide6.QtWidgets import (
    QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from PySide6.QtCore import Qt

# Clase generica, para generar una ventana externa que crea una tabla dependiendo de los datos necesarios para cada método
class VentanaTabla(QWidget):
    def __init__(self, titulo, encabezados, filas, decimales=4): # decimales ajustables
        super().__init__()
        self.setWindowTitle(titulo)
        self.resize(800, 600)

        tabla = QTableWidget(len(filas), len(encabezados)) # tras calcularse se saba la cantidad de filas totales
        tabla.setHorizontalHeaderLabels(encabezados) # cantidad de columnas
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)  # solo lectura

        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                if isinstance(valor, float):
                    texto = f"{valor:.{decimales}f}"
                else:
                    texto = str(valor)
                celda = QTableWidgetItem(texto)
                celda.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tabla.setItem(i, j, celda) # arma la tabla

        self.resumen = QLabel(f"Se detuvo tras {len(filas)} iteraciones") # como en cada metodo se llaman distinto no se puede mostrar mas

        layout = QVBoxLayout(self)
        layout.addWidget(tabla)
        layout.addWidget(self.resumen)
        self.tabla = tabla