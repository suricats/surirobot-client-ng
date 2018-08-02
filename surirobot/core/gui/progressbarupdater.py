import logging
import os
import queue
import time

from PyQt5.QtCore import QThread, pyqtSignal

from surirobot.core.common import QSuperTimer, ehpyqtSlot


class progressBarUpdater(QThread):
    """
    Provides a QtProgressBar updater with a QTimer
    """
    signal_value = pyqtSignal(int)
    def __init__(self, bar, timer, text=None):
        """
        Create a new instance of progressBarUpdater

        Parameters
        ----------
        bar : QProgressBar
            Progress bar that needs to be updated

        timer : QSuperTimer

        text : QLabel
        """
        QThread.__init__(self)
        self.q = queue.Queue()
        self.logger = logging.getLogger(type(self).__name__)
        self.bar = bar
        self.debug = int(os.environ.get('DEBUG', '0'))
        self.running = False
        self.timer = timer
        self.timer.started.connect(self.launch)
        self.timer.timeout.connect(self.hide_and_stop)
        self.timer.stopped.connect(self.hide_and_stop)
        if text:
            self.text = text
        self.counting = False
        self.signal_value.connect(self.bar.setValue)
    def __del__(self):
        self.quit()

    def run(self):
        try:
            # Main loop
            while True:
                # Blocking the thread
                self.running = self.q.get()
                if int(os.environ.get('DEBUG', '0')) >= 2:
                    self.logger.debug('START LOOP')
                while self.running:
                    if self.bar.isHidden():
                        self.bar.show()
                    if self.text:
                        if self.text.isHidden():
                            self.text.show()
                    value = (self.timer.elapsed() / self.timer.interval()) * 100
                    self.signal_value.emit(value)
                    time.sleep(0.01)
                if int(os.environ.get('DEBUG', '0')) >= 2:
                    self.logger.debug('END LOOP')
        except Exception as e:
            self.logger.error('{} occurred in progressBarUpdater.\n{} '.format(type(e).__name__, e))

    @ehpyqtSlot()
    def launch(self):
        self.q.put(True)

    @ehpyqtSlot()
    def hide_and_stop(self):
        self.running = False
        if not self.bar.isHidden():
            self.bar.hide()
            if self.text:
                self.logger.debug('BA')
                self.text.hide()



