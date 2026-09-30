import os
import sys
import ctypes
from ctypes import wintypes
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu
from PySide6.QtGui import QPixmap, QAction, QPainter, QPainterPath
from PySide6.QtCore import Qt, QPoint, QTimer, QRectF

MOD_CONTROL = 0x0002
VK_SPACE = 0x20
WM_HOTKEY = 0x0312
HOTKEY_ID = 1001

INTERVALO_MS = 30000  # 30 segundos de intervalo entre expresiones

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 320)

        # Configuración de ventana: frameless, transparente y siempre al frente
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.expresiones = [
            "feliz", "zen", "agotada",
            "triste", "concentrada", "cafe",
            "eureka", "enamorada", "enojada"
        ]
        self.indice_actual = 0

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        # Contenedor visual
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.resize(320, 320)

        self.actualizar_sprite()

        # Control de arrastre
        self._drag_pos = QPoint()

        # Temporizador automático (30 segundos)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.siguiente_expresion)
        self.timer.start(INTERVALO_MS)

        # Hotkey global (Ctrl + Espacio)
        self._hotkey_registrado = False
        self.registrar_hotkey()

    def registrar_hotkey(self):
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        if user32.RegisterHotKey(hwnd, HOTKEY_ID, MOD_CONTROL, VK_SPACE):
            self._hotkey_registrado = True

    def desregistrar_hotkey(self):
        if self._hotkey_registrado:
            hwnd = int(self.winId())
            ctypes.windll.user32.UnregisterHotKey(hwnd, HOTKEY_ID)
            self._hotkey_registrado = False

    def actualizar_sprite(self):
        nombre_expresion = self.expresiones[self.indice_actual]
        sprite_path = os.path.join(self.assets_dir, f"{nombre_expresion}.png")

        if os.path.exists(sprite_path):
            pixmap_original = QPixmap(sprite_path)
            
            scaled = pixmap_original.scaled(
                300, 300,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            circular = QPixmap(300, 300)
            circular.fill(Qt.GlobalColor.transparent)

            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

            path = QPainterPath()
            path.addEllipse(QRectF(0, 0, 300, 300))
            painter.setClipPath(path)

            x = (300 - scaled.width()) // 2
            y = (300 - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.end()

            self.label.setPixmap(circular)
        else:
            self.label.setText(f"Falta: {nombre_expresion}.png")

    def siguiente_expresion(self):
        self.indice_actual = (self.indice_actual + 1) % len(self.expresiones)
        self.actualizar_sprite()
        # Reiniciar temporizador para evitar saltos inmediatos tras un cambio manual
        self.timer.start(INTERVALO_MS)

    def nativeEvent(self, eventType, message):
        msg = wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
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
        self.desregistrar_hotkey()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AyeonApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
