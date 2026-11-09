import os

from PySide6.QtWidgets import (QCheckBox, QFileDialog, QHBoxLayout, QLabel,
                               QPushButton, QWidget)

from core.decal import stamp
from core.image_loader import load_image
from ui.decal_view import DecalView
from ui.qt_utils import hint_label, labeled_slider, side_panel


class DecalPage(QWidget):
    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.decal = None
        self.view = DecalView()

        side, lay = side_panel()
        lay.addWidget(hint_label(
            "Load a PNG with transparency, then click on the texture to stamp it.\n\n"
            "Wheel: zoom\nRight/middle drag: pan"))
        load_btn = QPushButton("Load decal...")
        self.decal_label = QLabel("No decal loaded")
        self.decal_label.setStyleSheet("color: #929aaa;")
        lay.addWidget(load_btn)
        lay.addWidget(self.decal_label)
        self.size_s = labeled_slider(lay, "Size", 5, 400, 100, "{}%")
        self.rot_s = labeled_slider(lay, "Rotation", -180, 180, 0, "{} deg")
        self.opa_s = labeled_slider(lay, "Opacity", 5, 100, 100, "{}%")
        self.wrap_check = QCheckBox("Wrap around edges")
        self.wrap_check.setChecked(True)
        lay.addWidget(self.wrap_check)
        lay.addStretch()

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.view, 1)
        root.addWidget(side)

        load_btn.clicked.connect(self.load_decal)
        for s in (self.size_s, self.rot_s, self.opa_s):
            s.valueChanged.connect(self._params_changed)
        self.view.stamp_requested.connect(self.on_stamp)
        doc.texture_changed.connect(self.refresh)
        self._params_changed()

    def refresh(self):
        if self.doc.texture is not None:
            self.view.set_image(self.doc.texture)

    def _params(self):
        return self.size_s.value() / 100, self.rot_s.value(), self.opa_s.value() / 100

    def _params_changed(self, *_):
        self.view.set_params(*self._params())

    def load_decal(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load decal", "", "Images (*.png *.webp *.tif *.tiff)")
        if not path:
            return
        try:
            self.decal = load_image(path)
        except Exception as err:
            self.doc.status.emit(str(err))
            return
        self.view.set_decal(self.decal)
        h, w = self.decal.shape[:2]
        self.decal_label.setText(f"{os.path.basename(path)} ({w} x {h})")

    def on_stamp(self, x, y):
        if self.decal is None or self.doc.texture is None:
            self.doc.status.emit("Load a decal first")
            return
        scale, angle, opacity = self._params()
        self.doc.set_texture(stamp(self.doc.texture, self.decal, (x, y), scale, angle,
                                   opacity, self.wrap_check.isChecked()))
