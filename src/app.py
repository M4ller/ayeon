import json
import os
import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu, QSystemTrayIcon
from PySide6.QtGui import QAction, QGuiApplication, QIcon
from PySide6.QtCore import Qt, QPoint, QTimer

from sprites import GestorSprites
from hotkey import WindowsHotkeyManager

INTERVALO_MS = 30000
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

class AyeonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayeon Companion")
        self.setFixedSize(320, 320)

        self.hotkey_mgr = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.gestor_sprites = GestorSprites()
        self.indice_actual = 0

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.resize(320, 320)

        self.actualizar_sprite()
        self.restaurar_posicion()

        self._drag_pos = QPoint()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.siguiente_expresion)
        self.timer.start(INTERVALO_MS)

        self.hotkey_mgr = WindowsHotkeyManager(int(self.winId()))
        self.hotkey_mgr.registrar()

        # Configuración del System Tray
        self.crear_tray_icon()

    def crear_tray_icon(self):
        """Inicializa el icono de la bandeja del sistema."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Icono base desde los sprites existentes
        pixmap = self.gestor_sprites.obtener_pixmap_circular(self.gestor_sprites.expresiones[0], diametro=64)
        if pixmap:
            self.tray_icon.setIcon(QIcon(pixmap))

        tray_menu = QMenu()
        self.accion_mostrar = QAction("Ocultar", self)
        self.accion_mostrar.triggered.connect(self.alternar_visibilidad)
        tray_menu.addAction(self.accion_mostrar)

        tray_menu.addSeparator()

        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.close)
        tray_menu.addAction(accion_salir)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activado)
        self.tray_icon.show()

    def alternar_visibilidad(self):
        """Muestra u oculta la ventana según su estado actual."""
        if self.isVisible():
            self.hide()
            self.accion_mostrar.setText("Mostrar")
        else:
            self.show()
            self.accion_mostrar.setText("Ocultar")

    def tray_activado(self, reason):
        """Clic simple o doble en la bandeja alterna visibilidad."""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.alternar_visibilidad()

    def restaurar_posicion(self):
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
        if pos_x is None or pos_y is None or pos_x < 0 or pos_x > pantalla.width() - 50:
            pos_x = pantalla.width() - self.width() - 40
            pos_y = pantalla.height() - self.height() - 40

        self.move(pos_x, pos_y)

    def guardar_posicion(self):
        pos = self.pos()
        data = {"x": pos.x(), "y": pos.y()}
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def cambiar_expresion_por_indice(self, indice: int):
        if 0 <= indice < len(self.gestor_sprites.expresiones):
            self.indice_actual = indice
            self.actualizar_sprite()
            self.timer.start(INTERVALO_MS)

    def actualizar_sprite(self):
        nombre = self.gestor_sprites.expresiones[self.indice_actual]
        pixmap = self.gestor_sprites.obtener_pixmap_circular(nombre, diametro=300)
        if pixmap:
            self.label.setPixmap(pixmap)
        else:
            self.label.setText(f"Falta: {nombre}.png")

    def siguiente_expresion(self):
        total = len(self.gestor_sprites.expresiones)
        self.cambiar_expresion_por_indice((self.indice_actual + 1) % total)

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

        menu_expresiones = menu.addMenu("Expresión")
        for i, nombre in enumerate(self.gestor_sprites.expresiones):
            accion = QAction(nombre.capitalize(), self)
            if i == self.indice_actual:
                accion.setText(f"✓ {nombre.capitalize()}")
            accion.triggered.connect(lambda checked=False, idx=i: self.cambiar_expresion_por_indice(idx))
            menu_expresiones.addAction(accion)

        menu.addSeparator()

        action_ocultar = QAction("Ocultar a la bandeja", self)
        action_ocultar.triggered.connect(self.alternar_visibilidad)
        menu.addAction(action_ocultar)

        action_salir = QAction("Salir", self)
        action_salir.triggered.connect(self.close)
        menu.addAction(action_salir)

        menu.exec(event.globalPos())

    def closeEvent(self, event):
        self.guardar_posicion()
        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()
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
