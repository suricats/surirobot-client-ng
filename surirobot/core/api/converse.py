from .base import ApiCaller
from .filedownloader import FileDownloader
from PyQt5.QtCore import QByteArray, QJsonDocument, QVariant, QFile, QIODevice, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest,QNetworkAccessManager
import uuid
from surirobot.services import serv_ap
from surirobot.core.common import State


class ConverseApiCaller(ApiCaller):
    download = pyqtSignal(str)
    play_sound = pyqtSignal(str)
    new_intent = pyqtSignal(int, 'QByteArray')

    def __init__(self, url='https://www.google.fr'):
        ApiCaller.__init__(self, url)

        self.intentMode = False
        self.fileDownloader = FileDownloader()
        self.fileDownloader.new_file.connect(self.downloadFinished)
        self.download.connect(self.fileDownloader.sendRequest)
        self.play_sound.connect(serv_ap.play)
        self.networkManager = QNetworkAccessManager(self)
        self.networkManager.finished.connect(self.receiveReply)
    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        buffer = QByteArray(reply.readAll())
        if (reply.error() != QNetworkReply.NoError):
            print("Error  " + str(reply.error()) + " : " + buffer.data().decode('utf8'))
            self.networkManager.clearAccessCache()
        jsonObject = QJsonDocument.fromJson(buffer).object()
        if self.intentMode:
            intent = jsonObject["intent"].toString()
            if (intent == "say-yes"):
                print("OUI INTENT")
                self.new_intent.emit(State.STATE_CONFIRMATION_YES, intent)
            if (intent == "say-no"):
                print("OUI INTENT")
                self.new_intent.emit(State.STATE_CONFIRMATION_NO, intent)
        else:
            message = jsonObject["answerText"].toString()
            url = jsonObject["answerAudioLink"].toString()
            if (message):
                print("Received from Converse API : " + message)
                self.new_reply.emit(message)
            else:
                self.new_reply.emit("Je ne me sens pas bien... [ERROR Conv : Field message needed but doesn't exist.]")
            if(url):
                print("Downloading the sound : " + url)
                self.download.emit(url)

        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, filepath):
        multiPart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        # Language
        textPart = QHttpPart()
        textPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"language\""))
        textPart.setBody(QByteArray().append(self.DEFAULT_LANGUAGE))
        # Audio
        audioPart = QHttpPart()
        audioPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"audio\"; filename=\"audio.wav\""))
        audioPart.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("audio/x-wav"))
        file = QFile(filepath)
        file.open(QIODevice.ReadOnly)

        audioPart.setBodyDevice(file)
        file.setParent(multiPart)  # we cannot delete the file now, so delete it with the multiPart

        # Id
        idPart = QHttpPart()
        idPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"userId\""))
        idPart.setBody(QByteArray().append("1"))
        multiPart.append(audioPart)
        multiPart.append(textPart)
        multiPart.append(idPart)
        request = QNetworkRequest(QUrl(self.url))
        print("Sended to Converse API : " + "File - " + file.fileName() + " - " + str(file.size() / 1000) + "Ko")
        self.isBusy = True
        reply = self.networkManager.post(request, multiPart)
        multiPart.setParent(reply)

    def start(self):
        ApiCaller.start(self)
        self.fileDownloader.start()

    def stop(self):
        self.fileDownloader.stop()
        ApiCaller.stop(self)

    @pyqtSlot('QByteArray')
    def downloadFinished(self, data):
        print("Download finished.")
        filename = self.TMP_DIR + uuid.uuid4() + ".wav"
        file = QFile(filename)
        if (not file.open(QIODevice.WriteOnly)):
            print("Could not create file : " + filename)
            return
        file.write(data)
        print("Sound file generated at : " + filename)
        file.close()

        # Play the audio
        # Restart the audioplayer
        self.play_sound.emit(filename)
