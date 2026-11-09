from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMainWindow,
                               QMessageBox, QPushButton, QTabWidget, QVBoxLayout, QWidget)

from core.exporter import export_image
from core.image_loader import load_image
from models.document import Document
from ui.pages.decal_page import DecalPage
from ui.pages.extract_page import ExtractPage
from ui.pages.seamless_page import SeamlessPage

STYLE = """
QMainWindow, QWidget { background-color: #17191f; color: #ffffff; }
QLabel { background: transparent; }
QPushButton { background-color: #303540; color: white; border: none;
              padding: 9px 16px; border-radius: 6px; }
QPushButton:hover { background-color: #454c5c; }
QPushButton:disabled { background-color: #22252d; color: #666d7a; }
QComboBox { background-color: #303540; padding: 6px; border-radius: 6px; }
QComboBox QAbstractItemView { background-color: #303540; selection-background-color: #454c5c; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: #22252d; color: #aab2c0; padding: 10px 22px; margin-right: 2px;
               border-top-left-radius: 6px; border-top-right-radius: 6px; }
QTabBar::tab:selected { background: #303540; color: white; }
QTabBar::tab:disabled { color: #555b68; }
QStatusBar { color: #929aaa; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.doc = Document()
        self.setWindowTitle("Texture Extractor")
        self.resize(1300, 800)
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLE)
        self._build()

        self.doc.texture_changed.connect(self._sync)
        self.doc.status.connect(self.statusBar().showMessage)
        for seq, fn in ((QKeySequence.StandardKey.Undo, self.undo),
                        (QKeySequence.StandardKey.Open, self.open_image)):
            sc = QShortcut(QKeySequence(seq), self)
            sc.activated.connect(fn)
        self._sync()
        self.statusBar().showMessage("Open or drop an image to begin")

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        header = QHBoxLayout()
        title = QLabel("TEXTURE EXTRACTOR")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.open_btn = QPushButton("Open Image")
        self.undo_btn = QPushButton("Undo")
        self.export_btn = QPushButton("Export Texture")
        header.addWidget(title)
        header.addStretch()
        for b in (self.open_btn, self.undo_btn, self.export_btn):
            header.addWidget(b)
        root.addLayout(header)

        self.extract_page = ExtractPage(self.doc)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.extract_page, "1  Extract")
        self.tabs.addTab(SeamlessPage(self.doc), "2  Seamless")
        self.tabs.addTab(DecalPage(self.doc), "3  Decals")
        root.addWidget(self.tabs, 1)

        self.open_btn.clicked.connect(self.open_image)
        self.undo_btn.clicked.connect(self.undo)
        self.export_btn.clicked.connect(self.export)
        self.extract_page.extracted.connect(lambda: self.tabs.setCurrentIndex(1))

    def _sync(self):
        has = self.doc.texture is not None
        self.tabs.setTabEnabled(1, has)
        self.tabs.setTabEnabled(2, has)
        self.export_btn.setEnabled(has)
        self.undo_btn.setEnabled(self.doc.can_undo())
        if not has:
            self.tabs.setCurrentIndex(0)

    # --- actions -------------------------------------------------------
    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open image", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff)")
        if path:
            self.load_path(path)

    def load_path(self, path):
        try:
            img = load_image(path)
        except Exception as err:
            QMessageBox.warning(self, "Open failed", str(err))
            return
        self.doc.set_source(img)
        self.tabs.setCurrentIndex(0)
        self.statusBar().showMessage(f"Loaded {path}  ({img.shape[1]} x {img.shape[0]})")

    def undo(self):
        self.doc.undo()

    def export(self):
        if self.doc.texture is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export texture", "texture.png", "PNG (*.png);;JPEG (*.jpg)")
        if path:
            try:
                self.statusBar().showMessage(f"Saved {export_image(path, self.doc.texture)}")
            except Exception as err:
                QMessageBox.warning(self, "Export failed", str(err))

    # --- drag & drop ---------------------------------------------------
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        urls = e.mimeData().urls()
        if urls:
            self.load_path(urls[0].toLocalFile())
