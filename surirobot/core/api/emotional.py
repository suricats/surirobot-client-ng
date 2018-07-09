from PyQt5.QtCore import pyqtSignal, QJsonDocument, QUrl, QVariant, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest

from surirobot.core.common import State, ehpyqtSlot
from .base import ApiCaller


class EmotionalAPICaller(ApiCaller):
    received_reply = pyqtSignal(int, dict)
    signalIndicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @ehpyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        buffer = reply.readAll()
        try:
            if reply.error() != QNetworkReply.NoError:
                print("EMOTIONAL - Error " + str(reply.error()))
                if reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute):
                    print("HTTP " + str(reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute) + ' : ' + str(buffer)))
                self.signalIndicator.emit("emotion", "red")
                self.networkManager.clearAccessCache()
                self.received_reply.emit(
                    State.EMOTION_NO, {'emotion': []}
                )
            else:
                jsonObject = QJsonDocument.fromJson(buffer).object()
                emotion = jsonObject["emotion"]
                # percent = jsonObject["percent"]

                self.signalIndicator.emit("emotion", "green")
                if emotion:
                    self.received_reply.emit(
                        State.EMOTION_NEW, {'emotion': emotion.toString()}
                        # State.EMOTION_NEW, {'emotion': 'angry'}
                    )
                else:
                    self.received_reply.emit(
                        State.EMOTION_NO, {'emotion': []}
                    )
            reply.deleteLater()
        except Exception as e:
            print("Error : " + str(e) + "\n" + str(buffer))

    @ehpyqtSlot(str)
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
