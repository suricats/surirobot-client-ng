from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager
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
        if (reply.error() != QNetworkReply.NoError):
            print("Error " + str(reply.error()) + reply.readAll())
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(reply.readAll()).object()

            emotion = jsonObject["data"]
            print(emotion)
            if emotion:
                self.received_reply.emit(
                    State.STATE_EMOTION_NEW, {'emotion': emotion.toString()}
                )
            else:
                self.received_reply.emit(
                    State.STATE_EMOTION_NO, {'emotion': []}
                )
        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, text):
        multiPart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        # Picture
        picturePart = QHttpPart()
        picturePart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"picture\"; filename=\"picture.jpeg\""))
        picturePart.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("image/jpeg"))
        file = QFile(text)
        file.open(QIODevice.ReadOnly)
        picturePart.setBodyDevice(file)
        file.setParent(multiPart)

        multiPart.append(picturePart)
        request = QNetworkRequest(QUrl(self.url))
        print("Sended to Emotional API : " + "File - " + file.fileName() + " - " + str(file.size() / 1000) + " Ko")
        reply = self.networkManager.post(request, multiPart)
        multiPart.setParent(reply)
