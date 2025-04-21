import sys
from PySide6.QtGui import QColor, QPainter, QTextFormat, QFont, QFontMetrics, QTextDocument, QTextCursor, QPageSize, QTextCharFormat, QTextFrameFormat, QTextTableFormat, QTextBlockFormat
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (QApplication, QTableWidget,
                               QTableWidgetItem, QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QFileDialog, QMessageBox, QSplitter, QTabWidget)
from PySide6.QtCore import Qt, QRect, QSize, Slot, QDateTime

from analizador import analizar_codigo
from sintactico import AnalizadorSintactico
from editor import CodeEditor
from error_log_terminal import ErrorLogTerminal

class AnalizadorLexicoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dictio =[]
        self.setWindowTitle("compLex")
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
        #self.texto_codigo = QPlainTextEdit(self)
        #self.texto_codigo.setPlaceholderText("Escribe el código aquí...")
        #layout.addWidget(self.texto_codigo)
        self.texto_codigo = CodeEditor()
        self.texto_codigo.setPlaceholderText("Escribe el código aquí...")
        self.texto_codigo.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.texto_codigo.setStyleSheet("background-color: #f0f0f0; color: #000000;")
        #layout.addWidget(self.texto_codigo)
        
        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Lexema", "Línea", "Columna", "Patrón", "Reservada"])
        #layout.addWidget(self.tabla)

        # Terminal
        #self.terminal = QTextEdit(self)
        #self.terminal.setPlaceholderText("Salida de la terminal...")
        #layout.addWidget(self.terminal)

        self.error_log = ErrorLogTerminal() # <--- Aquí se crea
        self.error_log.add_message("Terminal de historial iniciada.", level="INFO")
        #layout.addWidget(self.error_log) # <--- Aquí se añade al layout

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabs.addTab(self.error_log, "Historial")
        self.tabs.addTab(self.tabla, "Tabla de Resultados")
        # --- Splitter para dividir Editor y Log ---
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.texto_codigo)         # Área superior en el splitter
        #splitter.addWidget(self.error_log)     # Historial en la parte inferior
        splitter.addWidget(self.tabs)         # Área inferior en el splitter
        splitter.setStretchFactor(0, 3)        # Dar más espacio inicial al editor (3 partes)
        splitter.setStretchFactor(3, 1)        # Dar menos espacio inicial al log (1 parte)
        splitter.setSizes([500, 200])          # Tamaños iniciales aproximados en píxeles
        layout.addWidget(splitter)             # Añadir el splitter al layout principal


        menu = self.menuBar()
        self.archivo_actual = None
        file_menu = menu.addMenu("&File")
        file_menu.addAction("&Open", self.abrir_archivo)
        file_menu.addAction("&Save", self.guardar_archivo)
        file_menu.addAction("&Exportar a PDF", self.exportar_a_pdf)
        analizar_menu = menu.addMenu("&Analizar")
        analizar_menu.addAction("&Lexico", self.procesar_codigo)
        analizar_menu.addAction("&Sintactico", self.procesar_codigo2)

        

    def abrir_archivo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos de texto (*.txt);;Todos los archivos (*)")
        with open(filename, 'r') as file:
            contenido = file.read()
            self.texto_codigo.setPlainText(contenido)
        self.archivo_actual = filename
        self.setWindowTitle(f"Analizador Léxico - {filename}")
        self.error_log.add_message(f"Archivo abierto: {filename}", level="INFO")
    
    def guardar_archivo(self):
        if self.archivo_actual:
            with open(self.archivo_actual, 'w') as file:
                contenido = self.texto_codigo.toPlainText()
                file.write(contenido)
                print(f"Archivo guardado en {self.archivo_actual}")
                self.error_log.add_message(f"Archivo guardado: {self.archivo_actual}", level="INFO")

    def procesar_codigo(self):
        codigo = self.texto_codigo.toPlainText()
        tokens = analizar_codigo(codigo)
        self.dictio=[tokens]
        self.actualizar_tabla(tokens)
        for token in tokens:
            self.error_log.add_message(f"Token: {token['Lexema']}, ID: {token['ID']}, Línea: {token['Línea']}, Columna: {token['Columna']}, Patrón: {token['Patrón']}, Reservada: {'Sí' if token['Reservada'] else 'No'}", level="INFO")
        self.error_log.add_message("Análisis léxico completado.", level="INFO")
        self.error_log.add_message(f"Tokens encontrados: {len(tokens)}", level="INFO")
        

    def actualizar_tabla(self, resultados):
        self.tabla.setRowCount(len(resultados))
        for row, resultado in enumerate(resultados):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(resultado["ID"])))
            self.tabla.setItem(row, 1, QTableWidgetItem(resultado["Lexema"]))
            self.tabla.setItem(row, 2, QTableWidgetItem(str(resultado["Línea"])))
            self.tabla.setItem(row, 3, QTableWidgetItem(str(resultado["Columna"])))
            self.tabla.setItem(row, 4, QTableWidgetItem(resultado["Patrón"]))
            self.tabla.setItem(row, 5, QTableWidgetItem("Sí" if resultado["Reservada"] else "No"))

                
    def procesar_codigo2(self):
        codigo = self.texto_codigo.toPlainText()
        tokens = analizar_codigo(codigo)
        
        # Filtrar tokens irrelevantes
        tokens_filtrados = [t for t in tokens if t['ID'] not in [
            'whitespace', 
            'comentario_linea', 
            'comentario_bloque'
        ]]
        
        try:
            analizador = AnalizadorSintactico(tokens_filtrados)
            errores = analizador.analizar()
            if not errores:
                print("¡Análisis sintáctico exitoso!")
            else:
                print("\nErrores encontrados:")
                self.error_log.add_message("Errores encontrados:", level="ERROR")
                for error in errores:
                    print(error)
                    self.error_log.add_message(error, level="ERROR")
                    
        except Exception as e:
            print(f"Error crítico: {str(e)}")   
            self.error_log.add_message(f"Error crítico: {str(e)}", level="ERROR")
        self.error_log.add_message(f"Tokens analizados: {len(tokens_filtrados)}", level="INFO")
        self.error_log.add_message(f"Errores encontrados: {len(errores)}", level="INFO")
        self.error_log.add_message("Análisis sintáctico completado.", level="INFO") 

    def exportar_a_pdf(self):
        """Exporta el contenido del QPlainTextEdit a un archivo PDF"""
        # Configurar el diálogo para guardar archivo
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDefaultSuffix("pdf")
        file_dialog.setNameFilter("Archivos PDF (*.pdf)")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            
            # Crear el documento para PDF
            document = QTextDocument()
            cursor = QTextCursor(document)
            
            # Configurar formato del documento
            font = QFont()
            font.setPointSize(10)
            document.setDefaultFont(font)
            
            # --- Estilos predefinidos ---
            # Estilo para título principal
            title_format = QTextCharFormat()
            title_format.setFontPointSize(16)
            title_format.setFontWeight(QFont.Weight.Bold)
            title_format.setVerticalAlignment(QTextCharFormat.AlignMiddle)
            
            # Estilo para encabezados de sección
            section_format = QTextCharFormat()
            section_format.setFontPointSize(12)
            section_format.setFontWeight(QFont.Weight.Bold)
            section_format.setForeground(QColor(0, 0, 139))  # Azul oscuro
            section_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
            
            # Estilo para código
            code_format = QTextCharFormat()
            code_format.setFontFamily("Courier New")
            code_format.setFontPointSize(10)
            
            # Fondo para bloque de código
            code_block_format = QTextBlockFormat()
            code_block_format.setBackground(QColor(240, 240, 240))
            code_block_format.setTopMargin(10)
            code_block_format.setBottomMargin(10)
            code_block_format.setLeftMargin(10)
            code_block_format.setRightMargin(10)
            
            # Estilo para tabla
            table_format = QTextCharFormat()
            table_format.setFontPointSize(9)
            
            # Estilo para logs de error
            error_format = QTextCharFormat()
            error_format.setFontPointSize(9)
            error_format.setFontItalic(True)
            error_format.setForeground(QColor(139, 0, 0))  # Rojo oscuro

            
            # --- Contenido del PDF ---
            # Título del documento
            cursor.setCharFormat(title_format)
            cursor.insertText("Informe Completo\n")
            
            # Fecha
            normal_format = QTextCharFormat()
            normal_format.setFontPointSize(10)
            cursor.setCharFormat(normal_format)
            cursor.insertText(f"Generado el: {QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm')}\n\n")
            
            # Sección 1: Código fuente
            cursor.setCharFormat(section_format)
            cursor.insertText("CÓDIGO FUENTE\n")
            
            # Bloque de código con fondo
            cursor.insertBlock(code_block_format)
            cursor.setCharFormat(code_format)
            cursor.insertText(self.texto_codigo.toPlainText())
            cursor.insertBlock()  # Nueva línea sin fondo
            
            # Espacio entre secciones
            cursor.setCharFormat(normal_format)
            cursor.insertText("\n\n")
            
            # Sección 2: Datos tabulares
            cursor.insertText("DATOS TABULARES\n", section_format)
            cursor.insertText("\n")

            # Crear tabla en el PDF
            table = cursor.insertTable(
                self.tabla.rowCount() + 1,  # +1 para encabezados
                self.tabla.columnCount(),
                QTextTableFormat()
            )
            
            # Formato de la tabla
            table_format = table.format()
            table_format.setHeaderRowCount(1)
            table_format.setBorder(1)
            table_format.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
            table_format.setCellSpacing(2)
            table_format.setCellPadding(5)
            table_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            table.setFormat(table_format)
            
            # Crear formato para encabezados
            header_format = QTextCharFormat()
            header_format.setFontWeight(QFont.Weight.Bold)
            header_format.setBackground(QColor(220, 220, 220))
            header_format.setFontPointSize(10)
            
            # Crear formato para datos
            data_format = QTextCharFormat()
            data_format.setFontPointSize(9)
            
            # Llenar encabezados de tabla
            for col in range(self.tabla.columnCount()):
                header_item = self.tabla.horizontalHeaderItem(col)
                if header_item:  # Verificar si el encabezado existe
                    cell = table.cellAt(0, col)
                    cell_cursor = cell.firstCursorPosition()
                    cell_cursor.setCharFormat(header_format)
                    cell_cursor.insertText(header_item.text())
            
            # Llenar datos de la tabla
            for row in range(self.tabla.rowCount()):
                for col in range(self.tabla.columnCount()):
                    cell = table.cellAt(row + 1, col)  # +1 por la fila de encabezado
                    cell_cursor = cell.firstCursorPosition()
                    cell_cursor.setCharFormat(data_format)
            
                    item = self.tabla.item(row, col)
                    if item and item.text():  # Verificar si el item existe y tiene texto
                        cell_cursor.insertText(item.text())
                    else:
                        cell_cursor.insertText("-")  # Marcador para celdas vacías
            
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText("\n\n")
            
            # Sección 3: Logs de error
            cursor.insertText("REGISTRO DE ERRORES\n", section_format)
            cursor.insertText("\n")
            
            # Insertar logs con formato especial
            cursor.insertBlock(code_block_format)
            cursor.setCharFormat(error_format)
            cursor.insertText(self.error_log.get_log_text())
            cursor.insertText("\n\n")
            #error_block.mergeCharFormat(error_format)

            #Este es el bloque de código que se encarga de insertar la tabla de resultados y el log de errores en el PDF
            #table1 = self.tabla
            #cursor.insertText("Tabla de Resultados\n\n")
            #for row in range(table1.rowCount()):
            #    for col in range(table1.columnCount()):
            #        cursor.insertText(table1.item(row, col).text() + "\t")
            #    cursor.insertText("\n")
            #cursor.insertText(ErrorLogTerminal.get_log_text(self.error_log) + "\n\n")
            
            # Configurar la impresora (PDF)
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            #printer.setPageMargins(15, 15, 15, 15, QPrinter.Unit.Millimeter)
            
            # Exportar a PDF
            document.print_(printer)
            
            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Éxito", 
                                  f"El archivo PDF se ha guardado correctamente en:\n{file_path}")
        else:
            QMessageBox.warning(self, "Advertencia", 
                              "La operación de exportación ha sido cancelada.")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AnalizadorLexicoUI()
    ventana.show()
    sys.exit(app.exec())

