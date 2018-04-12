from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest,QNetworkAccessManager
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QJsonDocument, QUrl, QVariant, QFile, QIODevice
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

            emotion = jsonObject["data"]
            print(emotion)
            if emotion:
                self.received_reply.emit(
                    State.STATE_EMOTION_NEW, {'emotion': [emotion]}
                )
            else:
                self.received_reply.emit(
                    State.STATE_EMOTION_NO, {'emotion': []}
                )
        self.isBusy = False
        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, text):
        self.isBusy = True

        multiPart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        # Picture
        picturePart = QHttpPart()
        picturePart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"picture\"; filename=\"picture.jpeg\""))
        picturePart.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("image/jpeg"))
        file = QFile(text)
        file.open(QIODevice.ReadOnly)
        picturePart.setBodyDevice(file)
        multiPart.append(picturePart)

        request = QNetworkRequest(QUrl(self.url))

        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.networkManager.post(request, multiPart)
        print('yolo')
