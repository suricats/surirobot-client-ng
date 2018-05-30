from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QJsonDocument, QUrl, QVariant, QFile, QIODevice, QByteArray
from surirobot.core.common import State


class EmotionalAPICaller(ApiCaller):
    received_reply = pyqtSignal(int, dict)
    signalIndicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        print("huho")
        try:
            if (reply.error() != QNetworkReply.NoError):
                print("EMOTIONAL - Error " + str(reply.error()))
                print("HTTP " + str(reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute) + ' : ' + str(reply.readAll())))
                self.signalIndicator.emit("emotion", "red")
                self.networkManager.clearAccessCache()
            else:
                jsonObject = QJsonDocument.fromJson(reply.readAll()).object()
                print(jsonObject)
                emotion = jsonObject["emotion"]
                percent = jsonObject["percent"]

                self.signalIndicator.emit("emotion", "green")
                if emotion:
                    self.received_reply.emit(
                        State.EMOTION_NEW, {'emotion': emotion.toString()}
                    )
                else:
                    self.received_reply.emit(
                        State.EMOTION_NO, {'emotion': []}
                    )
            reply.deleteLater()
        except Exception as e:
            print("Error : "  + str(e))

    @pyqtSlot(str)
    def sendRequest(self, text):
        try:
            file = QFile(text)
            file.open(QIODevice.ReadOnly)
            body = file.readAll()
            request = QNetworkRequest(QUrl(self.url))
            request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("image/jpeg"))
            print("Sended to Emotional API : " + "File - " + file.fileName() + " - " + str(file.size() / 1000) + " Ko")
            self.networkManager.post(request, body)
        except Exception as e:
            print(e)
