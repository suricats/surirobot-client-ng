import sys
import shared as s
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


class Gui():
    def start(self):
        app = QApplication(sys.argv)
        w = QWidget()
        b = QLabel(w)
        b.setText("Hello World!")
        w.setGeometry(100, 100, 200, 50)
        b.move(50, 20)
        w.setWindowTitle("PyQt")
        w.showFullScreen()
        app.exec_()
