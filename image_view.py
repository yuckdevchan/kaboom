import sys, random, os, subprocess, ctypes, platform
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from pathlib import Path
from PIL import Image, ImageQt

if platform.system() == "Windows":
    import keyboard

from scripts.config_tools import get_program_directory

class ImageViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QHBoxLayout(self)

        self.scaling_methods = ["Nearest Neighbor", "Bilinear", "Bicubic", "Lanczos"]
        self.theme = "light"

        self.menubar = QtWidgets.QMenuBar()
        self.file_menu = self.menubar.addMenu("&File")
        self.open_action = self.file_menu.addAction("&Open")
        self.open_action.triggered.connect(self.select_image)
        self.exit_action = self.file_menu.addAction("&Exit")
        self.exit_action.setIcon(QtGui.QIcon(str(get_program_directory() / "images" / f"exit-{self.theme}.svg")))
        self.edit_menu = self.menubar.addMenu("&Edit")
        self.scaling_menu = self.edit_menu.addMenu("&Scaling Method")
        self.scaling_actions = [QAction(method, self) for method in self.scaling_methods]
        for action in self.scaling_actions:
            self.scaling_menu.addAction(action)
        self.exit_action.triggered.connect(self.close)
        self.layout.setMenuBar(self.menubar)

        self.open_action.setShortcut("Ctrl+O")
        self.exit_action.setShortcut("Ctrl+Q")
        
        self.options_layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.options_layout)

        self.scaling_method_layout = QtWidgets.QHBoxLayout()
        self.options_layout.addLayout(self.scaling_method_layout)

        self.scaling_method_text = QtWidgets.QLabel("Scaling Method")
        self.scaling_method_layout.addWidget(self.scaling_method_text)

        self.scaling_combobox = QtWidgets.QComboBox()
        self.scaling_combobox.addItems(self.scaling_methods)
        self.scaling_combobox.setCurrentIndex(1)
        self.scaling_combobox.currentIndexChanged.connect(self.update_image)
        self.scaling_method_layout.addWidget(self.scaling_combobox)

        self.scaling_method_layout.addStretch()

        self.pathbar_layout = QtWidgets.QHBoxLayout()
        self.options_layout.addLayout(self.pathbar_layout)

        self.pathbar_text = QtWidgets.QLabel("Image Path")
        self.pathbar_layout.addWidget(self.pathbar_text)

        self.pathbar = QtWidgets.QLineEdit()
        self.pathbar.setText("C:\\Users\\ethan\\Downloads\\gigi-AEgvTRJXm-U-unsplash.jpg")
        self.pathbar.returnPressed.connect(self.update_image)
        self.pathbar_layout.addWidget(self.pathbar)

        self.path_select_button = QtWidgets.QPushButton("Select Image")
        self.path_select_button.clicked.connect(self.select_image)
        self.pathbar_layout.addWidget(self.path_select_button)

        self.image_scene = QtWidgets.QGraphicsScene()
        self.image_view = QtWidgets.QGraphicsView(self.image_scene)
        self.image_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.image_view.setStyleSheet("QScrollBar:vertical { width: 10px; } QScrollBar:horizontal { height: 10px; }")
        self.image_view.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.image_view.setInteractive(True)
        self.layout.addWidget(self.image_view)

        self.options_layout.addStretch()
        self.layout.addStretch()

        QtWidgets.QApplication.instance().installEventFilter(self)
        self.update_image()
        keyboard.on_release_key('space', self.close_on_space)
        self.toggle_window()
        self.toggle_window()

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def select_image(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", str(Path.home() / "Pictures"), "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)")[0]
        if path:
            self.pathbar.setText(path.replace("/", "\\"))
            self.update_image()

    def update_image(self):
            scaling_method = self.scaling_combobox.currentText()
            path = self.pathbar.text()
            if os.path.exists(path):
                img = Image.open(path)
                if scaling_method == "Nearest Neighbor":
                    resample_method = Image.NEAREST
                elif scaling_method == "Bilinear":
                    resample_method = Image.BILINEAR
                elif scaling_method == "Bicubic":
                    resample_method = Image.BICUBIC
                elif scaling_method == "Lanczos":
                    resample_method = Image.LANCZOS

                img = img.resize((self.width(), self.height()), resample=resample_method)

                qimg = ImageQt.ImageQt(img)
                pixmap = QtGui.QPixmap.fromImage(qimg)

                # Add the pixmap to the scene
                self.image_scene.clear()
                self.image_scene.addPixmap(pixmap)
            else:
                self.text.setText("File not found")

    def wheelEvent(self, event):
        # Zoom in or out when the scroll wheel is used
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
    
        # Save the scene pos
        old_pos = self.image_view.mapToScene(event.position().toPoint())
    
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.image_view.scale(zoom_factor, zoom_factor)
    
        # Get the new position
        new_pos = self.image_view.mapToScene(event.position().toPoint())
    
        # Move scene to old position
        delta = new_pos - old_pos
        self.image_view.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        self.image_view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.image_view.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def close_on_space(self, event):
        print("Space Released")
        self.hide()
        os._exit(0)
