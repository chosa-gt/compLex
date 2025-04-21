# error_log_terminal.py (o en el mismo archivo de tu UI principal)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PySide6.QtCore import QDateTime, Qt

class ErrorLogTerminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Ajusta márgenes si es necesario

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)  # <-- Clave: No editable por el usuario
        self.log_output.setMaximumBlockCount(5000) # Opcional: Limitar historial para no consumir demasiada memoria

        # --- Estilo tipo terminal (Opcional) ---
        font = QFont("Consolas", 10) # O "Courier New", "Monaco", etc.
        self.log_output.setFont(font)
        palette = self.log_output.palette()
        # palette.setColor(palette.ColorRole.Base, QColor(30, 30, 30)) # Fondo oscuro
        # palette.setColor(palette.ColorRole.Text, QColor(220, 220, 220)) # Texto claro
        palette.setColor(palette.ColorRole.Base, QColor(245, 245, 245)) # Fondo claro (predeterminado)
        palette.setColor(palette.ColorRole.Text, QColor(50, 50, 50))    # Texto oscuro (predeterminado)
        self.log_output.setPalette(palette)
        # --------------------------------------

        layout.addWidget(self.log_output)
        self.setLayout(layout)

    def add_message(self, message, level="INFO"):
        """
        Añade un mensaje formateado al historial.
        Args:
            message (str): El mensaje a añadir.
            level (str): El nivel del mensaje ('INFO', 'WARN', 'ERROR', 'DEBUG', etc.).
                         Se usa para formateo visual (opcional).
        """
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        prefix = f"[{timestamp}] [{level.upper()}] "

        # Mover cursor al final para asegurar que appendPlainText funcione como se espera
        # y para aplicar formato si es necesario.
        cursor = self.log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)

        # Formato de color según el nivel (opcional)
        char_format = QTextCharFormat()
        if level.upper() == "ERROR":
            char_format.setForeground(QColor("red"))
        elif level.upper() == "WARN":
            char_format.setForeground(QColor(200, 100, 0)) # Naranja oscuro
        elif level.upper() == "DEBUG":
             char_format.setForeground(QColor("gray"))
        # else: INFO usa el color por defecto

        # Insertar prefijo con formato
        cursor.insertText(prefix, char_format)

        # Insertar el mensaje principal (sin formato especial aquí, hereda el último)
        # Si quieres resetear formato, crea un char_format normal aquí
        cursor.insertText(message + "\n") # Añade el salto de línea

        # Asegurar que la última línea sea visible (auto-scroll)
        self.log_output.ensureCursorVisible()

    def clear_log(self):
        """Limpia el contenido del log (para uso interno del programa si es necesario)."""
        self.log_output.clear()

    # Puedes añadir más métodos si necesitas, por ejemplo, para guardar el log a un archivo.
    # def save_log_to_file(self, filename):
    #    with open(filename, 'w', encoding='utf-8') as f:
    #        f.write(self.log_output.toPlainText())