import os
import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 400)

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

def main():
    app = QApplication(sys.argv)
    window = AyeonApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
