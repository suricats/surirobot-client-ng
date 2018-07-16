from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from surirobot.core.common import Dir, ehpyqtSlot


class ApiCaller(QObject):
    TMP_DIR = Dir.TMP
    DEFAULT_LANGUAGE = 'fr'
    DEFAULT_LANGUAGE_EXT = 'fr-FR'
    new_reply = pyqtSignal(str)

    def __init__(self, url='https://www.google.fr'):
        QObject.__init__(self)
        self.url = url
        self.currentThread = QThread()
        self.moveToThread(self.currentThread)

    def __del__(self):
        self.stop()

    def start(self):
        self.currentThread.start()

    def stop(self):
        self.currentThread.quit()
