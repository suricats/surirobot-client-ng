from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager
from abc import abstractmethod


class ApiCaller(QObject):
    TMP_DIR = 'tmp/'
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

    @pyqtSlot('QNetworkReply*')
    @abstractmethod
    def receiveReply(self, reply):
        pass

    def start(self):
        pass

    def stop(self):
        pass
