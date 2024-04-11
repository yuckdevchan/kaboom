import sys, random, os, subprocess, ctypes, platform
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QTimer
from pathlib import Path

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

        if os.path.exists("C:\\Program Files\\kaboom"):
            self.text.setText("kaboom is already installed.")
            self.install_button.setText("Update / Repair")
            self.install_button.clicked.disconnect()
            self.install_button.clicked.connect(self.update)

            self.reset_settings_button = QtWidgets.QPushButton("Reset settings")
            self.reset_settings_button.clicked.connect(self.reset_settings_confirmation)
            self.buttons_layout.addWidget(self.reset_settings_button)            

    def reset_settings_confirmation(self):
        # qmessage box
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Are you sure you want to reset settings?")
        msg.setInformativeText("This will delete all your settings.")
        msg.setWindowTitle("Reset settings")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.exec()
        if msg.result() == QtWidgets.QMessageBox.Ok:
            self.reset_settings()

    def reset_settings(self):
        config_path = Path(os.getenv("LOCALAPPDATA")) / "kaboom" / "config.toml"
        if config_path.exists():
            config_path.unlink()
        # qmessagebox
        settings_have_been_reset_msg = QtWidgets.QMessageBox()
        settings_have_been_reset_msg.setIcon(QtWidgets.QMessageBox.Information)
        settings_have_been_reset_msg.setText("Settings have been reset.")
        settings_have_been_reset_msg.setInformativeText("Click 'OK' to exit.")
        settings_have_been_reset_msg.setWindowTitle("Settings reset")
        settings_have_been_reset_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        settings_have_been_reset_msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        settings_have_been_reset_msg.buttonClicked.connect(lambda: sys.exit())
        settings_have_been_reset_msg.exec()

    def update(self):
        self.install_button.setEnabled(False)
        self.install_button.setText("Updating...")
        self.text.setText("Updating kaboom...")
        print("Updating kaboom...")
        os.chdir("C:\\Program Files\\kaboom")
        subprocess.run("git fetch --all")
        self.text.setText("kaboom has been updated.")
        print("kaboom has been updated.")
        self.finished("updated / repaired")

    def install(self):
        self.install_button.setEnabled(False)
        self.install_button.setText("Installing...")
        self.text.setText("Checking if git is installed...")
        if os.system("git --version") == 0:
            self.text.setText("Git is installed. Moving on...")
            print("Git is installed. Moving on...")
        else:
            self.text.setText("Git is not installed. Installing git...")
            print("Git is not installed. Installing git...")
            subprocess.run("winget install git -e")
        if os.path.exists(Path("C:\\Program Files\\Everything\\Everything.exe")):
            self.text.setText("Everything is installed. Moving on...")
            print("Everything is installed. Moving on...")
        else:
            self.text.setText("Everything is not installed. Installing Everything...")
            print("Everything is not installed. Installing Everything...")
            subprocess.run("winget install --id=voidtools.Everything  -e")
        if os.path.exists(Path("C:\\Program Files\\VideoLAN\\VLC\\vlc.exe")):
            self.text.setText("VLC is installed. Moving on...")
            print("VLC is installed. Moving on...")
        else:
            self.text.setText("VLC is not installed. Installing VLC...")
            print("VLC is not installed. Installing VLC...")
            subprocess.run("winget install --id=videolan.VLC -e")
        QTimer.singleShot(100, self.clone_repo_and_install)

    def clone_repo_and_install(self):
        subprocess.run("git clone https://github.com/yuckdevchan/kaboom.git kaboom-install")
        self.text.setText("Repository cloned. Installing kaboom...")
        subprocess.run('move kaboom-install \"C:\\Program Files\\kaboom"', shell=True)
        self.text.setText("kaboom installed. Creating start menu shortcut...")
        subprocess.run(f"{sys.executable} \"C:\\Program Files\\kaboom\\scripts\\create_lnk.py\"")
        self.text.setText("Shortcut created. kaboom has been installed.")
        self.finished("installed")
    
    def finished(self, action):
        finished_msg = QtWidgets.QMessageBox()
        finished_msg.setIcon(QtWidgets.QMessageBox.Information)
        finished_msg.setText(f"kaboom has been {action}.")
        finished_msg.setInformativeText("Click 'OK' to exit.")
        finished_msg.setWindowTitle(f"kaboom {action}")
        finished_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        finished_msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        finished_msg.buttonClicked.connect(lambda: sys.exit())
        finished_msg.exec()

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
