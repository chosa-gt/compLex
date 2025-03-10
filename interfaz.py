import sys
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QTableWidget,
                               QTableWidgetItem, QMainWindow, QLineEdit, QWidget, QVBoxLayout, QTextEdit, QPushButton)
from analizador import analizar_codigo

class AnalizadorLexicoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Analizador Léxico")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)
        
        # Cuadro de texto
        self.texto_codigo = QTextEdit(self)
        self.texto_codigo.setPlaceholderText("Escribe el código aquí...")
        layout.addWidget(self.texto_codigo)
        
        # Botón para procesar
        self.boton_procesar = QPushButton("Procesar", self)
        layout.addWidget(self.boton_procesar)
        self.boton_procesar.clicked.connect(self.procesar_codigo)
        
        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Lexema", "Línea", "Columna", "Patrón", "Reservada"])
        layout.addWidget(self.tabla)

    def procesar_codigo(self):
        codigo = self.texto_codigo.toPlainText()
        resultados = analizar_codigo(codigo)
        self.actualizar_tabla(resultados)

    def actualizar_tabla(self, resultados):
        self.tabla.setRowCount(len(resultados))
        for row, resultado in enumerate(resultados):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(resultado["ID"])))
            self.tabla.setItem(row, 1, QTableWidgetItem(resultado["Lexema"]))
            self.tabla.setItem(row, 2, QTableWidgetItem(str(resultado["Línea"])))
            self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado["Columna"])))
            self.tabla.setItem(row, 4, QTableWidgetItem(resultado["Patrón"]))
            self.tabla.setItem(row, 5, QTableWidgetItem("Sí" if resultado["Reservada"] else "No"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AnalizadorLexicoUI()
    ventana.show()
    sys.exit(app.exec())
