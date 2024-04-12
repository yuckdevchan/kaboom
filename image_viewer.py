import sys
from PySide6.QtWidgets import QApplication
from main import ImageViewer

if __name__ == '__main__':
    # qt boilerplate
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec())