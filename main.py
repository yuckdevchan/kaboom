import sys, win32gui, win32con, config
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPainterPath
from PySide6 import QtCore, QtWidgets, QtGui

from utils import list_programs, narrow_down, determine_program

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"background-color: {config.bg_colour}; color: {config.text_colour};")
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.textbox = QtWidgets.QLineEdit(self)
        self.label = QtWidgets.QLabel(self)
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.label)
        self.textbox.textChanged.connect(self.on_text_changed)
        self.textbox.returnPressed.connect(self.on_enter_pressed)
        program_list = list_programs()
        text = ""
        for i in range(len(program_list)):
            text += program_list[i].replace(".lnk", "").rsplit("\\")[-1] + "\n"
        self.change_text(text)

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
    widget.show()

    sys.exit(app.exec())