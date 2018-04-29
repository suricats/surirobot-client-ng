from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager
from abc import abstractmethod
from surirobot.core.common import Dir


class ApiCaller(QObject):
    TMP_DIR = Dir.TMP
    DEFAULT_LANGUAGE = 'fr'
    DEFAULT_LANGUAGE_EXT = 'fr-FR'
    new_reply = pyqtSignal(str)

    def __init__(self, url='https://www.google.fr'):
        QObject.__init__(self)
        self.url = url
        self.networkManager = QNetworkAccessManager(self)
        self.networkManager.finished.connect(self.receiveReply)
        self.currentThread = QThread()
        self.moveToThread(self.currentThread)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    @abstractmethod
    def receiveReply(self, reply):
        pass

    def start(self):
        self.currentThread.start()

    def stop(self):
        self.currentThread.quit()
