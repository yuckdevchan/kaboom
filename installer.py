import sys, random, os, subprocess, ctypes, platform
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QTimer

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.text = QtWidgets.QLabel("Welcome to kaboom online installer. Click 'Install' to start installing kaboom.", alignment=QtCore.Qt.AlignCenter)
        font = self.text.font()
        font.setBold(True)
        self.text.setFont(font)
        self.layout.addWidget(self.text)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(sys.exit)
        self.buttons_layout.addWidget(self.cancel_button)

        self.install_button = QtWidgets.QPushButton("Install")
        self.install_button.clicked.connect(self.install)
        self.buttons_layout.addWidget(self.install_button)

        self.layout.addLayout(self.buttons_layout)

    def install(self):
        self.install_button.setEnabled(False)
        self.install_button.setText("Installing...")
        self.text.setText("Checking if git is installed...")
        if os.system("git --version") == 0:
            self.text.setText("Git is installed. Cloning repository...")
        else:
            self.text.setText("Git is not installed. Installing git...")
            subprocess.run("winget install git -e")
        if os.path.exists("kaboom"):
            os.system("rmdir /s /q kaboom")
        QTimer.singleShot(100, self.clone_repo_and_install)

    def clone_repo_and_install(self):
        subprocess.run("git clone https://github.com/yuckdevchan/kaboom.git")
        self.text.setText("Repository cloned. Installing kaboom...")
        if os.path.exists("C:\\Program Files\\kaboom"):
            os.system("rmdir /s /q \"C:\\Program Files\\kaboom\"")
        subprocess.run('move kaboom \"C:\\Program Files\\\"')
        # run Program Files/kaboom/scripts/create_lnk.py
        self.text.setText("kaboom installed. Creating start menu shortcut...")
        subprocess.run(f"{sys.executable} \"C:\\Program Files\\kaboom\\scripts\\create_lnk.py\"")

if __name__ == "__main__":
    if platform.system() != "Windows":
        raise Exception("This script is for Windows only")
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(500, 400)
    widget.setWindowTitle("kaboom Online Installer")
    widget.show()

    sys.exit(app.exec())
