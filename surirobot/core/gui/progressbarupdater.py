from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer, QElapsedTimer
from PyQt5 import QtGui, QtWidgets
import time


class progressBarUpdater(QThread):
    def __init__(self, bar, timer, counter, text=None):
        QThread.__init__(self)
        self.bar = bar
        self.timer = timer
        self.counter = counter
        if text:
            self.text = text
        self.counting = False

    def __del__(self):
        self.quit()

    def run(self):
        try:
            while(True):
                if self.timer.isActive():
                    if self.bar.isHidden():
                        self.bar.show()
                    if self.text:
                        if self.text.isHidden():
                            self.text.show()
                    self.bar.setProperty("value", (self.counter.elapsed()/self.timer.interval())*100)
                elif not self.bar.isHidden():
                    self.bar.hide()
                    if self.text:
                        self.text.hide()
                time.sleep(0.01)
        except Exception as e:
            print('progressBarUpdater : ' + str(e))
