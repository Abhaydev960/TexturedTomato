from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from ui.qt_utils import to_pixmap

PAN_BUTTONS = (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton)


class ImageView(QGraphicsView):
    """Zoomable/pannable view of a numpy RGBA image.
    Wheel = zoom, middle/right mouse drag = pan. Left click is free for tools.
    Scene coordinates == image pixel coordinates."""

    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene(self)  # NOT self.scene: that shadows QGraphicsView.scene()
        self.setScene(self._scene)
        self.image_item = QGraphicsPixmapItem()
        self._scene.addItem(self.image_item)
        self._shape = None
        self._pending_fit = False
        self._pan_last = None
        self._cursor = Qt.CursorShape.ArrowCursor

        self.setBackgroundBrush(QColor("#17191f"))
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewport().setMouseTracking(True)

    # --- image ---------------------------------------------------------
    def set_image(self, rgba, fit=None):
        h, w = rgba.shape[:2]
        if fit is None:
            fit = self._shape != (h, w)
        self._shape = (h, w)
        self.image_item.setPixmap(to_pixmap(rgba))
        self._scene.setSceneRect(-w * 0.5, -h * 0.5, w * 2, h * 2)  # room to pan
        if fit:
            self._pending_fit = True
            if self.isVisible():
                QTimer.singleShot(0, self.fit)

    def fit(self):
        if self._shape is None:
            return
        self.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
        self._pending_fit = False
        self._update_hint()

    def showEvent(self, e):
        super().showEvent(e)
        if self._pending_fit:  # fit requested while on a hidden tab
            QTimer.singleShot(0, self.fit)

    def set_base_cursor(self, cursor):
        self._cursor = cursor
        self.viewport().setCursor(cursor)

    def _update_hint(self):
        # crisp pixels when zoomed in, smooth when zoomed out
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,
                           self.transform().m11() < 1)

    # --- zoom / pan ----------------------------------------------------
    def wheelEvent(self, e):
        f = 1.15 if e.angleDelta().y() > 0 else 1 / 1.15
        if 0.02 < self.transform().m11() * f < 64:
            self.scale(f, f)
            self._update_hint()

    def mousePressEvent(self, e):
        if e.button() in PAN_BUTTONS:
            self._pan_last = e.position().toPoint()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            e.accept()
            return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._pan_last is not None:
            p = e.position().toPoint()
            d = p - self._pan_last
            self._pan_last = p
            hb, vb = self.horizontalScrollBar(), self.verticalScrollBar()
            hb.setValue(hb.value() - d.x())
            vb.setValue(vb.value() - d.y())
            e.accept()
            return
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() in PAN_BUTTONS and self._pan_last is not None:
            self._pan_last = None
            self.viewport().setCursor(self._cursor)
            e.accept()
            return
        super().mouseReleaseEvent(e)
