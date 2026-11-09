from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget

from core.seamless import make_seamless, tile_preview
from ui.image_view import ImageView
from ui.qt_utils import hint_label, labeled_slider, side_panel


class SeamlessPage(QWidget):
    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.view = ImageView()

        side, lay = side_panel()
        lay.addWidget(hint_label(
            "Offsets the texture by half and cross-fades the borders so it tiles "
            "without a visible seam.\n\nTurn on the 3x3 preview to check the result."))
        self.width_slider = labeled_slider(lay, "Blend width", 10, 100, 50, "{}%")
        apply_btn = QPushButton("Make seamless")
        self.tile_check = QCheckBox("Preview 3x3 tiling")
        lay.addWidget(apply_btn)
        lay.addWidget(self.tile_check)
        lay.addStretch()

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.view, 1)
        root.addWidget(side)

        apply_btn.clicked.connect(self.apply)
        self.tile_check.toggled.connect(lambda _: self.refresh(fit=True))
        doc.texture_changed.connect(lambda: self.refresh())

    def refresh(self, fit=None):
        t = self.doc.texture
        if t is None:
            return
        self.view.set_image(tile_preview(t) if self.tile_check.isChecked() else t, fit)

    def apply(self):
        if self.doc.texture is None:
            return
        self.doc.set_texture(make_seamless(self.doc.texture, self.width_slider.value() / 100))
        self.doc.status.emit("Made seamless (Ctrl+Z to undo)")
