from PyQt5.QtCore import QThread, pyqtSlot, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import logging
import os
import queue


class AudioPlayer(QThread):
    def __init__(self):
        QThread.__init__(self)

        self.base_dir = os.getcwd()
        self.q = queue.Queue()
        self.player = QMediaPlayer()
        self.player.setVolume(100)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.wait()

    def run(self):
        while(True):
            url = self.q.get()
            sound = QMediaContent(url)
            self.player.setMedia(sound)
            self.player.play()

    @pyqtSlot(str)
    def play(self, filename):
        url = QUrl.fromLocalFile(self.base_dir + '/' + filename)
        self.q.put(url)
