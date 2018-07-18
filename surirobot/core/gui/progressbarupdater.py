from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets
import time
import logging

class progressBarUpdater(QThread):
    """
    Provides a QtProgressBar updater with a QTimer
    """
    def __init__(self, bar, timer, counter, text=None):
        """
        Create a new instance of progressBarUpdater

        Parameters
        ----------
        bar : QProgressBar
            Progress bar that needs to be updated

        timer : QTimer

        counter : QElapsedTimer

        text : QLabel
        """
        QThread.__init__(self)
        self.logger = logging.getLogger(type(self).__name__)
        self.bar = bar
        self.timer = timer
        self.counter = counter
        if text:
            self.text = text
        self.counting = False

    def __del__(self):
        self.quit()
        progressBarUpdater()

    def run(self):
        try:
            # Main loop
            while True:
                # Case:
                if self.timer.isActive():
                    if self.bar.isHidden():
                        self.bar.show()
                    if self.text:
                        if self.text.isHidden():
                            self.text.show()
                    value = (self.counter.elapsed() / self.timer.interval()) * 100
                    self.bar.setValue(value)
                elif not self.bar.isHidden():
                    self.bar.hide()
                    if self.text:
                        self.text.hide()
                time.sleep(0.01)
        except Exception as e:
            self.logger.error('{} occurred in progressBarUpdater.\n{} '.format(type(e).__name__, e))
