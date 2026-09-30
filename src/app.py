import json
import os
import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtCore import Qt, QPoint, QTimer

from sprites import GestorSprites
from hotkey import WindowsHotkeyManager

INTERVALO_MS = 30000  # 30 segundos entre expresiones
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 320)

        self.hotkey_mgr = None

        # Configuración de ventana: frameless, transparente y siempre visible
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Módulos desacoplados
        self.gestor_sprites = GestorSprites()
        self.indice_actual = 0

        # Contenedor visual
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.resize(320, 320)

        self.actualizar_sprite()

        # Restaurar posición previa o colocar en esquina inferior derecha
        self.restaurar_posicion()

        # Control de arrastre
        self._drag_pos = QPoint()

        # Temporizador automático (30 s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.siguiente_expresion)
        self.timer.start(INTERVALO_MS)

        # Gestor de atajo global (Ctrl + Espacio)
        self.hotkey_mgr = WindowsHotkeyManager(int(self.winId()))
        self.hotkey_mgr.registrar()

    def restaurar_posicion(self):
        """Carga las coordenadas guardadas en config.json o posiciona en la esquina inferior derecha."""
        pos_x, pos_y = None, None

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pos_x = data.get("x")
                    pos_y = data.get("y")
            except Exception:
                pass

        pantalla = QGuiApplication.primaryScreen().availableGeometry()

        # Si no hay datos válidos o quedan fuera de pantalla, ubicar abajo a la derecha
        if pos_x is None or pos_y is None or pos_x < 0 or pos_x > pantalla.width() - 50:
            pos_x = pantalla.width() - self.width() - 40
            pos_y = pantalla.height() - self.height() - 40

        self.move(pos_x, pos_y)

    def guardar_posicion(self):
        """Persiste la posición actual en config.json."""
        pos = self.pos()
        data = {"x": pos.x(), "y": pos.y()}
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def actualizar_sprite(self):
        nombre = self.gestor_sprites.expresiones[self.indice_actual]
        pixmap = self.gestor_sprites.obtener_pixmap_circular(nombre, diametro=300)
        if pixmap:
            self.label.setPixmap(pixmap)
        else:
            self.label.setText(f"Falta: {nombre}.png")

    def siguiente_expresion(self):
        total = len(self.gestor_sprites.expresiones)
        self.indice_actual = (self.indice_actual + 1) % total
        self.actualizar_sprite()
        self.timer.start(INTERVALO_MS)

    def nativeEvent(self, eventType, message):
        if self.hotkey_mgr is not None and self.hotkey_mgr.es_evento_hotkey(int(message)):
            self.siguiente_expresion()
            return True, 0
        return super().nativeEvent(eventType, message)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        action_salir = QAction("Salir", self)
        action_salir.triggered.connect(self.close)
        menu.addAction(action_salir)
        menu.exec(event.globalPos())

    def closeEvent(self, event):
        self.guardar_posicion()
        if self.hotkey_mgr is not None:
            self.hotkey_mgr.desregistrar()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AyeonApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
