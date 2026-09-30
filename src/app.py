import os
import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt, QPoint, QTimer

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 400)

        # Configuración de ventana: frameless, transparente y al frente
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Lista de expresiones ordenadas
        self.expresiones = [
            "feliz", "zen", "agotada",
            "triste", "concentrada", "cafe",
            "eureka", "enamorada", "enojada"
        ]
        self.indice_actual = 0

        # Directorio base de assets
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        # Contenedor visual
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.resize(320, 400)

        # Cargar sprite inicial
        self.actualizar_sprite()

        # Control para arrastrar la ventana
        self._drag_pos = QPoint()

        # Temporizador para alternar expresiones automáticamente (cada 5 segundos para pruebas)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.siguiente_expresion)
        self.timer.start(5000)

    def actualizar_sprite(self):
        nombre_expresion = self.expresiones[self.indice_actual]
        sprite_path = os.path.join(self.assets_dir, f"{nombre_expresion}.png")

        if os.path.exists(sprite_path):
            pixmap = QPixmap(sprite_path)
            scaled = pixmap.scaled(
                300, 380,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled)
        else:
            self.label.setText(f"Falta: {nombre_expresion}.png")

    def siguiente_expresion(self):
        self.indice_actual = (self.indice_actual + 1) % len(self.expresiones)
        self.actualizar_sprite()

    # Arrastre de ventana con clic izquierdo
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # Cierre con tecla Escape
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()

    # Menú contextual con clic derecho
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        action_salir = QAction("Salir", self)
        action_salir.triggered.connect(self.close)
        menu.addAction(action_salir)
        menu.exec(event.globalPos())

def main():
    app = QApplication(sys.argv)
    window = AyeonApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
