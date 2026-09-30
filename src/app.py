import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint, QTimer

from sprites import GestorSprites
from hotkey import WindowsHotkeyManager

INTERVALO_MS = 30000  # 30 segundos entre expresiones

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 320)

        # 1. Bandera y referencia del hotkey manager inicializadas antes de cualquier evento nativo
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

        # Control de arrastre
        self._drag_pos = QPoint()

        # Temporizador automático (30 s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.siguiente_expresion)
        self.timer.start(INTERVALO_MS)

        # 2. Registrar el hotkey global de forma segura
        self.hotkey_mgr = WindowsHotkeyManager(int(self.winId()))
        self.hotkey_mgr.registrar()

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
        # Proteger contra eventos tempranos antes de completar __init__
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
