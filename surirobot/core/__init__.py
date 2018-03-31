import sys
from PyQt5.QtWidgets import QApplication
from .gui.ui import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.smartShow()
