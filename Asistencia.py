import json

from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication, QHeaderView, QLabel, QMainWindow, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
from PySide6.QtCore import Qt

#
# Tabla de asistencias para la clase de Estructura de Datos
#

ATTENDANCE = 15

ARCHIVO = Path(__file__).with_name("Asistencias.json")

class TablaAsistencia(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asistencias del segundo parcial")
        self.resize(400, 550)

        self.tabla = QTableWidget(ATTENDANCE, 2) # 2 columnas
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Asistencia"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False)  # oculta los números de fila

        self.agregar_fila(0, "21/09/2026")
        self.agregar_fila(1, "23/09/2026")
        self.agregar_fila(2, "25/09/2026")
        self.agregar_fila(3, "28/09/2026")
        self.agregar_fila(4, "30/09/2026")
        self.agregar_fila(5, "02/10/2026")
        self.agregar_fila(6, "05/10/2026")
        self.agregar_fila(7, "07/10/2026")
        self.agregar_fila(8, "09/10/2026")
        self.agregar_fila(9, "12/10/2026")
        self.agregar_fila(10, "14/10/2026")
        self.agregar_fila(11, "16/10/2026")
        self.agregar_fila(12, "19/10/2026")
        self.agregar_fila(13, "21/10/2026")
        self.agregar_fila(14, "23/10/2026")

        self.etiqueta = QLabel()
        self.cargar()
        self.actualizar_conteo()
        self.tabla.itemChanged.connect(self.al_cambiar)

        # actualiza conteo
        self.tabla.itemChanged.connect(self.actualizar_conteo)

        centro = QWidget()
        layout = QVBoxLayout(centro)
        layout.addWidget(self.tabla)
        layout.addWidget(self.etiqueta)
        self.setCentralWidget(centro)

    def actualizar_conteo(self):
        asistencias = 0
        for fila in range(ATTENDANCE):
            if self.tabla.item(fila, 1).checkState() == Qt.Checked:
                asistencias += 1
        self.etiqueta.setText(f"Asistencias: {asistencias} de {ATTENDANCE}")

    def agregar_fila(self, fila, fecha_texto):
        # columna 0: la fecha (solo lectura)
        item_fecha = QTableWidgetItem(fecha_texto)
        item_fecha.setFlags(Qt.ItemIsEnabled)
        self.tabla.setItem(fila, 0, item_fecha)

        # columna 1:  checkboxses
        item_check = QTableWidgetItem()
        item_check.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item_check.setCheckState(Qt.Unchecked)
        self.tabla.setItem(fila, 1, item_check)

    def guardar(self):
        datos = {}
        for fila in range(ATTENDANCE):
            fecha = self.tabla.item(fila, 0).text()
            datos[fecha] = self.tabla.item(fila, 1).checkState() == Qt.Checked
        ARCHIVO.write_text(json.dumps(datos, indent=2), encoding="utf-8")

    def cargar(self):
        if not ARCHIVO.exists():
            return
        try:
            datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for fila in range(ATTENDANCE):
            fecha = self.tabla.item(fila, 0).text()
            if datos.get(fecha, False):
                self.tabla.item(fila, 1).setCheckState(Qt.Checked)

    def al_cambiar(self):
        self.actualizar_conteo()
        self.guardar()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = TablaAsistencia()
    ventana.show()
    sys.exit(app.exec())
