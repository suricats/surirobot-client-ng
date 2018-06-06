from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtGui import QProgressBar


class progressBarUpdater(QThread):
    def __init__(self, bar, timer):
        QThread.__init__(self)
        self.bar = bar

    def __del__(self):
        self.quit()

    def run(self):
        try:
            while(True):
                if not self.timer.isActive():
                    self.bar.hide()
                else:
                    pass
        except Exception as e:
            print('progressBarUpdater : ' + str(e))
