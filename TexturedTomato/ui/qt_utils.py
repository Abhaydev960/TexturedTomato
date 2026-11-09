import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget


def to_pixmap(rgba: np.ndarray) -> QPixmap:
    rgba = np.ascontiguousarray(rgba)
    h, w = rgba.shape[:2]
    return QPixmap.fromImage(QImage(rgba.data, w, h, 4 * w, QImage.Format.Format_RGBA8888))


def side_panel():
    w = QWidget()
    w.setFixedWidth(260)
    lay = QVBoxLayout(w)
    lay.setContentsMargins(12, 12, 12, 12)
    lay.setSpacing(10)
    return w, lay


def hint_label(text):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet("color: #929aaa;")
    return lbl


def labeled_slider(layout, text, lo, hi, value, fmt="{}"):
    row = QHBoxLayout()
    val = QLabel(fmt.format(value))
    row.addWidget(QLabel(text))
    row.addStretch()
    row.addWidget(val)
    s = QSlider(Qt.Orientation.Horizontal)
    s.setRange(lo, hi)
    s.setValue(value)
    s.valueChanged.connect(lambda v: val.setText(fmt.format(v)))
    layout.addLayout(row)
    layout.addWidget(s)
    return s
