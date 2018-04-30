from PyQt5.QtCore import QThread, pyqtSlot
import logging
import sys
import platform
import subprocess
from playsound import playsound

class AudioPlayer(QThread):
    def __init__(self):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.playObj = None

    def __del__(self):
        self.quit()

    @pyqtSlot(str)
    def play(self, filename):
        try:
            self.logger.info('Now playing' + str(filename) + '.')
            if platform.system() == "Darwin":
                subprocess.call(["afplay", filename])
            else:
                playsound(filename)
        except Exception as e:
            self.logger.info('Error : .' + str(e))
