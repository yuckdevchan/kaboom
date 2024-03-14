import sys, win32gui, win32con, config, keyboard, toml
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPainterPath
from PySide6 import QtCore, QtWidgets, QtGui

from utils import list_programs, narrow_down, determine_program

class SettingsPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config.program_title} Settings")
        self.setFixedSize(300, 200)

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Checkboxes layout
        self.checkboxes_layout = QtWidgets.QVBoxLayout()
        self.dark_mode_switch = QtWidgets.QCheckBox("Dark Mode", self)
        with open('config.toml', 'r') as file:
            toml_config = toml.load(file)
            if toml_config["Settings"]["dark_mode"]:
                self.dark_mode_switch.setChecked(True)
            else:
                self.dark_mode_switch.setChecked(False)
        self.borderless_switch = QtWidgets.QCheckBox("Borderless", self)
        self.borderless_switch.setChecked(config.borderless)
        self.rounded_corners_switch = QtWidgets.QCheckBox("Rounded Corners", self)
        self.rounded_corners_switch.setChecked(config.rounded_corners)
        self.always_on_top_switch = QtWidgets.QCheckBox("Always on Top", self)
        self.always_on_top_switch.setChecked(config.always_on_top)
        self.checkboxes_layout.addWidget(self.dark_mode_switch)
        self.checkboxes_layout.addWidget(self.borderless_switch)
        self.checkboxes_layout.addWidget(self.rounded_corners_switch)
        self.checkboxes_layout.addWidget(self.always_on_top_switch)

        # Slider layout
        self.slider_layout = QtWidgets.QHBoxLayout()
        self.opacity_label = QtWidgets.QLabel("Opacity:", self)
        self.opacity_slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(config.opacity * 100)
        self.slider_layout.addWidget(self.opacity_label)
        self.slider_layout.addWidget(self.opacity_slider)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.checkboxes_layout)
        self.main_layout.addLayout(self.slider_layout)

        # Connect signal for dark mode switch
        self.dark_mode_switch.stateChanged.connect(self.change_theme)

    def change_theme(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == Qt.Checked:
                config['Settings']['dark_mode'] = False  # Enable dark mode
            else:
                config['Settings']['dark_mode'] = True  # Disable dark mode
            file.seek(0)
            toml.dump(config, file)
            file.truncate()



class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        with open('config.toml', 'r') as file:
            config = toml.load(file)
            if config["Settings"]["dark_mode"]:
                bg_color = config["Settings"]["dark_mode_bg"]
                text_color = config["Settings"]["dark_mode_text"]
            else:
                bg_color = config["Settings"]["light_mode_bg"]
                text_color = config["Settings"]["light_mode_text"]
            self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.textbox_layout = QtWidgets.QHBoxLayout()
        self.textbox = QtWidgets.QLineEdit(self)
        self.settings_button = QtWidgets.QPushButton("Settings", self)
        self.label = QtWidgets.QLabel(self)
        
        self.textbox_layout.addWidget(self.textbox)
        self.textbox_layout.addWidget(self.settings_button)
        
        self.layout.addLayout(self.textbox_layout)
        self.layout.addWidget(self.label)
        
        self.textbox.textChanged.connect(self.on_text_changed)
        self.textbox.returnPressed.connect(self.on_enter_pressed)
        self.settings_button.clicked.connect(self.open_settings)
        
        program_list = list_programs()
        text = ""
        for i in range(len(program_list)):
            text += program_list[i].replace(".lnk", "").rsplit("\\")[-1] + "\n"
        self.change_text(text)

    def open_settings(self):
        settings_popup = SettingsPopup(self)
        settings_popup.exec_()

    def hide_window(self):
        widget.hide()

    def resizeEvent(self, event):
        if config.rounded_corners:
            self.setMask(self.createMask(self.rect()))

    def createMask(self, rect):
        if config.rounded_corners:
            mask = QtGui.QBitmap(rect.size())
            mask.fill(Qt.color0)

            painter = QtGui.QPainter(mask)
            painter.setBrush(Qt.color1)
            painter.drawRoundedRect(rect, 20, 20)
            painter.end()

        return mask

    @QtCore.Slot()
    def on_text_changed(self, text):
        narrowed_list = narrow_down(text)
        new_text = ""
        for i in range(len(narrowed_list)):
            new_text += narrowed_list[i].replace(".lnk", "").rsplit("\\")[-1] + "\n"
        self.change_text(new_text)

    @QtCore.Slot()
    def change_text(self, text):
        self.label.setText(text)
        self.label.setFixedHeight(200)

    @QtCore.Slot()
    def on_enter_pressed(self):
        if self.textbox.text() == "exit":
            sys.exit()
        elif self.label.text() == config.no_results_text + "\n":
            sys.exit()
        else:
            determine_program(self.textbox.text())
            sys.exit()

if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    app.setWindowIcon(QIcon("logo.png"))

    font = QtGui.QFont(config.font_family, config.font_size)
    app.setFont(font)

    widget = MyWidget()
    widget.resize(600, 1)
    if config.borderless:
        widget.setWindowFlags(Qt.FramelessWindowHint)
    if config.always_on_top:
        widget.setWindowFlags(Qt.WindowStaysOnTopHint)
    widget.setWindowTitle("kaboom")
    widget.setWindowOpacity(config.opacity)
    def mousePressEvent(event):
        widget.oldPos = event.globalPos()
    widget.show()

    sys.exit(app.exec())