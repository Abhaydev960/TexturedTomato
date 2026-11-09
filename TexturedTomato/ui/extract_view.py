from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem

from core.extractor import order_points
from ui.image_view import ImageView


class Handle(QGraphicsEllipseItem):
    """Draggable corner point that keeps a constant on-screen size."""

    def __init__(self, pos, on_move):
        super().__init__(-7, -7, 14, 14)
        self.on_move = on_move
        self.setPos(pos)
        self.setBrush(QColor("#4da3ff"))
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setZValue(10)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                      | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
                      | QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.on_move()
        return super().itemChange(change, value)


class ExtractView(ImageView):
    points_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.handles = []
        self.poly = QGraphicsPolygonItem()
        pen = QPen(QColor("#4da3ff"), 2)
        pen.setCosmetic(True)
        self.poly.setPen(pen)
        self.poly.setBrush(QColor(77, 163, 255, 40))
        self.poly.setZValue(5)
        self.poly.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._scene.addItem(self.poly)
        self.set_base_cursor(Qt.CursorShape.CrossCursor)

    def set_image(self, rgba, fit=None):
        super().set_image(rgba, fit)
        self.reset_points()

    def reset_points(self):
        for h in self.handles:
            self._scene.removeItem(h)
        self.handles.clear()
        self._update_poly()
        self.points_changed.emit(0)

    def get_points(self):
        if len(self.handles) < 4:
            return None
        return order_points([(h.pos().x(), h.pos().y()) for h in self.handles])

    def _update_poly(self):
        pts = [h.pos() for h in self.handles]
        if len(pts) == 4:
            pts = [QPointF(float(x), float(y))
                   for x, y in order_points([(p.x(), p.y()) for p in pts])]
        self.poly.setPolygon(QPolygonF(pts))

    def mousePressEvent(self, e):
        if (e.button() == Qt.MouseButton.LeftButton and self._shape
                and len(self.handles) < 4):
            pos = e.position().toPoint()
            if not isinstance(self.itemAt(pos), Handle):
                h = Handle(self.mapToScene(pos), self._update_poly)
                self._scene.addItem(h)
                self.handles.append(h)
                self._update_poly()
                self.points_changed.emit(len(self.handles))
                return
        super().mousePressEvent(e)
