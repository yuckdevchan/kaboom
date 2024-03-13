import sys
from PySide6.QtCore import Qt, Slot
from PySide6 import QtCore, QtWidgets, QtGui

from utils import list_programs, narrow_down, determine_program

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

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
            text += program_list[i] + "\n"
        self.change_text(text)

    @QtCore.Slot()
    def on_text_changed(self, text):
        narrowed_list = narrow_down(text)
        new_text = ""
        for i in range(len(narrowed_list)):
            new_text += narrowed_list[i] + "\n"
        print(new_text)
        self.change_text(new_text)

    @QtCore.Slot()
    def change_text(self, text):
        self.label.setText(text)
        self.label.setFixedHeight(200)

    @QtCore.Slot()
    def on_enter_pressed(self):
        print("Enter pressed")
        if self.textbox.text() == "exit":
            sys.exit()
        else:
            determine_program(self.textbox.text())

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(600, 1)
    widget.setWindowFlags(Qt.FramelessWindowHint)
    widget.show()

    sys.exit(app.exec())
