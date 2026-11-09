from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QWidget

from core.extractor import extract_quad
from ui.extract_view import ExtractView
from ui.qt_utils import hint_label, side_panel


class ExtractPage(QWidget):
    extracted = Signal()

    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.view = ExtractView()

        side, lay = side_panel()
        lay.addWidget(hint_label(
            "Click the 4 corners of the area you want to flatten. Drag the points to "
            "adjust.\n\nWheel: zoom\nRight/middle drag: pan"))
        lay.addWidget(QLabel("Output size"))
        self.size_combo = QComboBox()
        self.size_combo.addItem("Auto (keep aspect)", None)
        for s in (512, 1024, 2048):
            self.size_combo.addItem(f"{s} x {s}", s)
        lay.addWidget(self.size_combo)

        self.extract_btn = QPushButton("Extract texture")
        self.extract_btn.setEnabled(False)
        reset_btn = QPushButton("Reset points")
        whole_btn = QPushButton("Use whole image")
        lay.addWidget(self.extract_btn)
        lay.addWidget(reset_btn)
        lay.addWidget(whole_btn)
        lay.addStretch()

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.view, 1)
        root.addWidget(side)

        self.view.points_changed.connect(lambda n: self.extract_btn.setEnabled(n == 4))
        self.extract_btn.clicked.connect(self.extract)
        reset_btn.clicked.connect(self.view.reset_points)
        whole_btn.clicked.connect(self.use_whole)
        doc.source_changed.connect(self._on_source)

    def _on_source(self):
        if self.doc.source is not None:
            self.view.set_image(self.doc.source, fit=True)

    def extract(self):
        pts = self.view.get_points()
        if pts is None:
            return
        size = self.size_combo.currentData()
        try:
            out = extract_quad(self.doc.source, pts, (size, size) if size else None)
        except ValueError as err:
            self.doc.status.emit(str(err))
            return
        self.doc.set_texture(out)
        self.doc.status.emit(f"Extracted {out.shape[1]} x {out.shape[0]} texture")
        self.extracted.emit()

    def use_whole(self):
        if self.doc.source is not None:
            self.doc.set_texture(self.doc.source.copy())
            self.extracted.emit()
