from .base import ApiCaller
from PyQt5.QtCore import QJsonDocument, pyqtSlot, pyqtSignal, QVariant, QFile, QIODevice, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest

class SttApiCaller(ApiCaller):
    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        if (reply.error() != QNetworkReply.NoError):
            print("STT - Error  " + str(reply.error()))
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(reply.readAll()).object()

        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, filepath):
        pass
