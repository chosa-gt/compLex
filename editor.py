import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTextEdit
)
from PySide6.QtGui import QPainter, QColor, QTextFormat, QFont, QFontMetrics
from PySide6.QtCore import Qt, QRect, QSize, Slot
from analizador import analizar_codigo
from sintactico import AnalizadorSintactico

# --- Widget para el área de números de línea ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor # Referencia al editor principal

    def sizeHint(self):
        # Calcula el ancho necesario basado en el número de líneas
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        # Llama al método de pintura del editor principal
        self.codeEditor.lineNumberAreaPaintEvent(event)

# --- Widget principal del editor de código ---
class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        # Conectar señales a slots para actualizar el área de números de línea
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        # Establecer configuraciones iniciales
        self.updateLineNumberAreaWidth(0) # Establece el margen inicial
        self.highlightCurrentLine()        # Resalta la línea actual inicial
        # self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap) # Opcional: Desactivar ajuste de línea

        # Fuente monoespaciada recomendada para editores de código
        font = QFont("Courier New", 10) # O usa "Consolas", "Monaco", etc.
        self.setFont(font)
        self.lineNumberArea.setFont(font)


    def lineNumberAreaWidth(self):
        # Calcula el ancho necesario para mostrar los números de línea
        digits = 1
        max_lines = max(1, self.blockCount())
        while max_lines >= 10:
            max_lines //= 10
            digits += 1

        # Usa QFontMetrics para obtener el ancho del carácter más ancho ('9')
        # y añade un poco de padding
        font_metrics = QFontMetrics(self.font())
        # space = 5 + font_metrics.horizontalAdvance('9') * digits # Ancho basado en '9'
        space = 10 + font_metrics.averageCharWidth() * digits # Ancho basado en promedio + padding
        return space

    @Slot()
    def updateLineNumberAreaWidth(self, newBlockCount=0): # newBlockCount no se usa directamente aquí
        # Establece el margen izquierdo del viewport para dejar espacio
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @Slot(QRect, int)
    def updateLineNumberArea(self, rect, dy):
        # Actualiza el área de números de línea cuando el texto cambia o se hace scroll
        if dy:
            # Si hubo scroll vertical, desplaza el área de números
            self.lineNumberArea.scroll(0, dy)
        else:
            # Si no hubo scroll vertical (p.ej., cambio de texto, scroll horizontal),
            # repinta el área de números visible afectada por 'rect'
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        # Si la primera línea visible ha cambiado (p.ej., al añadir/eliminar líneas arriba),
        # recalcula el ancho por si acaso el número de dígitos cambió.
        if rect.contains(self.viewport().rect().topLeft()):
            self.updateLineNumberAreaWidth(0)


    def resizeEvent(self, event):
        # Llama al método base
        super().resizeEvent(event)

        # Actualiza la geometría (posición y tamaño) del área de números de línea
        # para que ocupe el espacio del margen izquierdo que hemos reservado
        cr = self.contentsRect() # Área interior del widget QPlainTextEdit
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        # Dibuja los números de línea
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(228, 228, 228)) # Color de fondo del área

        # Obtiene el primer bloque visible
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        # Calcula la posición Y superior del primer bloque visible
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        # Calcula la posición Y inferior del último bloque (aproximado)
        bottom = top + int(self.blockBoundingRect(block).height())

        # Itera sobre los bloques visibles
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1) # Número de línea (base 1)
                painter.setPen(Qt.GlobalColor.darkGray) # Color del texto de los números
                # Dibuja el número alineado a la derecha en el área
                painter.drawText(
                    0,                          # x
                    top,                        # y
                    self.lineNumberArea.width() - 5, # Ancho (con padding derecho)
                    self.fontMetrics().height(), # Alto
                    Qt.AlignmentFlag.AlignRight,  # Alineación
                    number                      # Texto
                )

            # Pasa al siguiente bloque
            block = block.next()
            # Actualiza la posición Y para el siguiente bloque
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    @Slot()
    def highlightCurrentLine(self):
        # Resalta la línea donde está el cursor
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.GlobalColor.yellow).lighter(160) # Color de resaltado
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)
