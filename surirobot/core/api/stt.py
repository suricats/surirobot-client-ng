from .base import ApiCaller
from PyQt5.QtCore import QJsonDocument, pyqtSlot, pyqtSignal, QVariant, QFile, QIODevice, QUrl, QByteArray
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest
from surirobot.core.common import State


class SttApiCaller(ApiCaller):

    updateState = pyqtSignal(str, int, dict)

    def __init__(self, url):
        ApiCaller.__init__(self, url)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        buffer = reply.readAll()
        if (reply.error() != QNetworkReply.NoError):
            print("STT - Error  " + str(reply.error()))
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(buffer).object()
            if jsonObject.get("code") and jsonObject.get("msg") and jsonObject.get("data") and jsonObject.get("confidence"):
                self.updateState.emit("converse", State.STATE_CONVERSE_NEW, {"intent": "@STT", "reply": jsonObject["data"]["text"][0].toString()})
            else:
                print('STT - Error : Invalid response format : ' + str(buffer))
                self.updateState.emit("converse", State.STATE_CONVERSE_NEW, {"intent": "dont-understand", "reply": "Je n'ai pas compris."})

        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, filepath):
        multiPart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        # Language
        textPart = QHttpPart()
        textPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"language\""))
        textPart.setBody(QByteArray().append(self.DEFAULT_LANGUAGE_EXT))
        # Audio
        audioPart = QHttpPart()
        audioPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"audio\"; filename=\"audio.wav\""))
        audioPart.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("audio/x-wav"))
        file = QFile(filepath)
        file.open(QIODevice.ReadOnly)

        audioPart.setBodyDevice(file)
        file.setParent(multiPart)  # we cannot delete the file now, so delete it with the multiPart

        multiPart.append(audioPart)
        multiPart.append(textPart)

        request = QNetworkRequest(QUrl(self.url))
        print("Sended to TTS API : " + "File - " + file.fileName() + " - " + str(file.size() / 1000) + "Ko")
        self.isBusy = True
        reply = self.networkManager.post(request, multiPart)
        multiPart.setParent(reply)
