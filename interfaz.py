import sys
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QTableWidget,
                               QTableWidgetItem, QMainWindow, QWidget, QGridLayout, QTextEdit, QPushButton, QPlainTextEdit, QFileDialog, QMessageBox)
from PySide6 import QtCore
from PySide6 import QtGui

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
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        #self.central_widget.setLayout(layout)
        
        # Editor de texto
        self.texto_codigo = QPlainTextEdit(self)
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

        # Terminal
        self.terminal = QTextEdit(self)
        self.terminal.setPlaceholderText("Salida de la terminal...")
        layout.addWidget(self.terminal)

        menu = self.menuBar()
        self.archivo_actual = None
        file_menu = menu.addMenu("&File")
        file_menu.addAction("&Open", self.abrir_archivo)
        file_menu.addAction("&Save", self.guardar_archivo)

        

    def abrir_archivo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos de texto (*.txt);;Todos los archivos (*)")
        with open(filename, 'r') as file:
            contenido = file.read()
            self.texto_codigo.setPlainText(contenido)
        self.archivo_actual = filename
        self.setWindowTitle(f"Analizador Léxico - {filename}")
    
    def guardar_archivo(self):
        if self.archivo_actual:
            with open(self.archivo_actual, 'w') as file:
                contenido = self.texto_codigo.toPlainText()
                file.write(contenido)
                print(f"Archivo guardado en {self.archivo_actual}")

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

