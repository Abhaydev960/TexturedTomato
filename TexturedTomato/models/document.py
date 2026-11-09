from PySide6.QtCore import QObject, Signal


class Document(QObject):
    """Shared state: source photo -> texture (extracted/seamless/decorated)."""
    source_changed = Signal()
    texture_changed = Signal()
    status = Signal(str)
    MAX_UNDO = 20

    def __init__(self):
        super().__init__()
        self.source = None
        self.texture = None
        self._undo = []

    def set_source(self, img):
        self.source, self.texture, self._undo = img, None, []
        self.source_changed.emit()
        self.texture_changed.emit()

    def set_texture(self, img):
        """Always pass a NEW array (core functions already return copies)."""
        if self.texture is not None:
            self._undo.append(self.texture)
            self._undo = self._undo[-self.MAX_UNDO:]
        self.texture = img
        self.texture_changed.emit()

    def can_undo(self):
        return bool(self._undo)

    def undo(self):
        if self._undo:
            self.texture = self._undo.pop()
            self.texture_changed.emit()
