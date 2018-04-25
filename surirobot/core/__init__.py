import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from .gui.ui import MainWindow
from .gui.new import Ui_MainWindow

# Load QT
app = QApplication(sys.argv)
ui = MainWindow()
ui.smartShow()
test_window = QMainWindow()
test_ui = Ui_MainWindow()
test_ui.setupUi(test_window)
test_window.show()
