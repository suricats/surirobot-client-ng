from .base import ApiCaller
from .filedownloader import FileDownloader
from PyQt5.QtCore import QByteArray, QJsonDocument, QVariant, QFile, QIODevice, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager
import uuid
from surirobot.services import serv_ap
from surirobot.core.common import State,Dir

class ConverseApiCaller(ApiCaller):
    download = pyqtSignal(str)
    play_sound = pyqtSignal(str)
    new_intent = pyqtSignal(int, 'QByteArray')
    updateState = pyqtSignal(str, int, dict)
    signalIndicator = pyqtSignal(str, str)

    def __init__(self, url='https://www.google.fr'):
        ApiCaller.__init__(self, url)

        self.fileDownloader = FileDownloader()
        self.fileDownloader.new_file.connect(self.downloadFinished)
        self.download.connect(self.fileDownloader.sendRequest)
        self.play_sound.connect(serv_ap.play)

        self.intent = ""
        self.message = ""

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        buffer = QByteArray(reply.readAll())
        # print('\nConverse : Receive reply : ' + str(buffer))
        if (reply.error() != QNetworkReply.NoError):
            print("Converse - Error  " + str(reply.error()) + " : ")
            print("HTTP " + str(reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)) + ' : ' + buffer.data().decode('utf8'))
            self.signalIndicator.emit("converse", "red")
            self.message = "Oh mince ! Je ne fonctionne plus très bien :("
            filename = Dir.DATA + "error.wav"
            self.updateState.emit("converse", State.CONVERSE_NEW, {"intent": "error", "reply": self.message, "audiopath": filename})
            self.networkManager.clearAccessCache()
        jsonObject = QJsonDocument.fromJson(buffer).object()
        # Converse reply
        if jsonObject.get("intent") and jsonObject.get("answerText") and jsonObject.get("answerAudioLink"):
            self.intent = jsonObject["intent"].toString()
            print("intent : " + self.intent)
            self.message = jsonObject["answerText"].toString()
            url = jsonObject["answerAudioLink"].toString()
            self.download.emit(url)
        elif jsonObject.get("field") and jsonObject.get("value") and jsonObject.get("userId"):
            print('Converse - updateMemory responded.')
        else:
            self.signalIndicator.emit("converse", "orange")
            print('Converse - Error : Invalid response format.\n' + str(buffer))
        reply.deleteLater()

    @pyqtSlot(str, str, int)
    def updateMemory(self, field, value, userId):
        # Create the json request
        jsonObject = {
            'field': field,
            'value': value,
            'userId': str(userId)
        }
        jsonData = QJsonDocument(jsonObject)
        data = jsonData.toJson()
        request = QNetworkRequest(QUrl(self.url + '/updateMemory'))
        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.isBusy = True
        self.networkManager.post(request, data)

    @pyqtSlot(str, int)
    @pyqtSlot(str)
    def sendRequest(self, filepath, id=1):
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
        idPart.setBody(QByteArray().append(str(id)))
        multiPart.append(audioPart)
        multiPart.append(textPart)
        multiPart.append(idPart)
        request = QNetworkRequest(QUrl(self.url+'/converse'))
        print("Sended to Converse API : " + "File - " + file.fileName() + " - " + str(file.size() / 1000) + "Ko")
        self.isBusy = True
        reply = self.networkManager.post(request, multiPart)
        multiPart.setParent(reply)

    def start(self):
        ApiCaller.start(self)
        self.fileDownloader.start()

    def stop(self):
        self.fileDownloader.currentThread.quit()
        super().stop()

    @pyqtSlot('QByteArray')
    def downloadFinished(self, data):
        print("Download finished.")
        filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
        file = QFile(filename)
        if (not file.open(QIODevice.WriteOnly)):
            print("Could not create file : " + filename)
            return
        file.write(data)
        print("Sound file generated at : " + filename)
        file.close()
        self.signalIndicator.emit("converse", "green")
        self.updateState.emit("converse", State.CONVERSE_NEW, {"intent": self.intent, "reply": self.message, "audiopath": filename})
        # Play the audio
        # Restart the audioplayer
        # self.play_sound.emit(filename)
