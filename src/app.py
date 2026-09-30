import os
import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt, QPoint

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 400)

        # Configuración de desktop companion: sin bordes, transparente y siempre visible
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ruta al sprite de prueba
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sprite_path = os.path.join(base_dir, "assets", "feliz.png")

        # Contenedor visual
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.resize(320, 400)

        if os.path.exists(sprite_path):
            pixmap = QPixmap(sprite_path)
            scaled = pixmap.scaled(
                300, 380,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled)
        else:
            self.label.setText("Sprite no encontrado")

        # Control para arrastrar la ventana
        self._drag_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # Cierre rápido con tecla Escape
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()

    # Cierre con clic derecho -> Salir
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
