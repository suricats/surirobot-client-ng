import sys
from PyQt5.QtWidgets import QApplication
from .gui.ui import MainWindow

# Load QT
app = QApplication(sys.argv)
ui = MainWindow()
ui.smartShow()
