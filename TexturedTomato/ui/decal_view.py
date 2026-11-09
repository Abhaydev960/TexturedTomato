from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem

from ui.image_view import ImageView
from ui.qt_utils import to_pixmap


class DecalView(ImageView):
    """Shows the texture with a live ghost of the decal under the cursor."""
    stamp_requested = Signal(float, float)  # image-pixel coords

    def __init__(self):
        super().__init__()
        self.ghost = QGraphicsPixmapItem()
        self.ghost.setZValue(10)
        self.ghost.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.ghost.hide()
        self._scene.addItem(self.ghost)
        self._last = None
        self.set_base_cursor(Qt.CursorShape.CrossCursor)

    def set_decal(self, rgba):
        if rgba is None:
            self.ghost.setPixmap(QPixmap())
            self.ghost.hide()
            return
        pm = to_pixmap(rgba)
        self.ghost.setPixmap(pm)
        self.ghost.setTransformOriginPoint(pm.width() / 2, pm.height() / 2)
        self._place()

    def set_params(self, scale, angle, opacity):
        self.ghost.setScale(scale)
        self.ghost.setRotation(angle)  # clockwise, matches core.decal
        self.ghost.setOpacity(opacity)

    def _place(self):
        pm = self.ghost.pixmap()
        if self._last is None or pm.isNull():
            self.ghost.hide()
            return
        self.ghost.setPos(self._last.x() - pm.width() / 2, self._last.y() - pm.height() / 2)
        self.ghost.show()

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)
        self._last = self.mapToScene(e.position().toPoint())
        self._place()

    def leaveEvent(self, e):
        self._last = None
        self.ghost.hide()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._shape:
            p = self.mapToScene(e.position().toPoint())
            self.stamp_requested.emit(p.x(), p.y())
            return
        super().mousePressEvent(e)
