import os
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF

EXPRESIONES_DISPONIBLES = [
    "feliz", "zen", "agotada",
    "triste", "concentrada", "cafe",
    "eureka", "enamorada", "enojada"
]

class GestorSprites:
    def __init__(self, assets_dir=None):
        if assets_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.assets_dir = os.path.join(base_dir, "assets")
        else:
            self.assets_dir = assets_dir

        self.expresiones = EXPRESIONES_DISPONIBLES

    def obtener_pixmap_circular(self, nombre_expresion: str, diametro: int = 300) -> QPixmap:
        """Carga el sprite, lo escala y le aplica una mascara circular con antialiasing."""
        sprite_path = os.path.join(self.assets_dir, f"{nombre_expresion}.png")
        if not os.path.exists(sprite_path):
            return None

        pixmap_original = QPixmap(sprite_path)
        scaled = pixmap_original.scaled(
            diametro, diametro,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        circular = QPixmap(diametro, diametro)
        circular.fill(Qt.GlobalColor.transparent)

        painter = QPainter(circular)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addEllipse(QRectF(0, 0, diametro, diametro))
        painter.setClipPath(path)

        x = (diametro - scaled.width()) // 2
        y = (diametro - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.end()

        return circular
