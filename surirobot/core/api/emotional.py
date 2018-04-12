from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QJsonDocument, QUrl, QVariant
from surirobot.core.common import State


class EmotionalAPICaller(ApiCaller):
    received_reply = pyqtSignal(int, dict)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        print('received')
        if (reply.error() != QNetworkReply.NoError):
            print("Error " + reply.error() + reply.readAll().toString())
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(reply.readAll())

            tmpAr = jsonObject["facial"].toArray()
            if tmpAr:
                self.received_reply.emit(
                    State.STATE_EMOTION_NEW, {'emotion': tmpAr}
                )
            else:
                self.received_reply.emit(
                    State.STATE_EMOTION_NO, {'emotion': []}
                )

        self.isBusy = False
        reply.deleteLater()

    @pyqtSlot(bytes)
    def sendRequest(self, text):
        self.isBusy = True
        jsonObject = {'pictures': str(text)}

        jsonData = QJsonDocument(jsonObject)
        data = jsonData.toJson()
        request = QNetworkRequest(QUrl(self.url))

        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.networkManager.post(request, data)
