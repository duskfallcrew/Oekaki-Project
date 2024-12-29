import sys
from PyQt6.QtWidgets import QApplication
from ui_main import OekakiApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OekakiApp()
    window.show()
    sys.exit(app.exec())
