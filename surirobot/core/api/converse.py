from .base import ApiCaller
from .filedownloader import FileDownloader
from PyQt5.QtCore import QByteArray, QJsonDocument, QVariant, QFile, QIODevice, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager
import uuid
from surirobot.services import serv_ap
from surirobot.core.common import State, Dir, ehpyqtSlot


class ConverseApiCaller(ApiCaller):
    download = pyqtSignal(str)
    play_sound = pyqtSignal(str)
    new_intent = pyqtSignal(int, 'QByteArray')
    update_state = pyqtSignal(str, int, dict)
    signalIndicator = pyqtSignal(str, str)

    def __init__(self, url):
        ApiCaller.__init__(self, url)

        self.fileDownloader = FileDownloader()
        self.fileDownloader.new_file.connect(self.downloadFinished)
        self.download.connect(self.fileDownloader.sendRequest)
        self.play_sound.connect(serv_ap.play)

        self.intent = ""
        self.message = ""

    def __del__(self):
        self.stop()

    @ehpyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        buffer = QByteArray(reply.readAll())
        # print('\nConverse : Receive reply : ' + str(buffer))
        if reply.error() != QNetworkReply.NoError:
            print("Converse - Error  " + str(reply.error()) + " : ")
            print("HTTP " + str(reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)) + ' : ' + buffer.data().decode('utf8'))
            self.signalIndicator.emit("converse", "red")
            self.message = "Oh mince ! Je ne fonctionne plus très bien :("
            filename = Dir.DATA + "error.wav"
            self.update_state.emit("converse", State.CONVERSE_NEW, {"intent": "error", "reply": self.message, "audiopath": filename})
            self.networkManager.clearAccessCache()
        jsonObject = QJsonDocument.fromJson(buffer).object()
        # Converse reply
        jsonObject = reply.rawHeader(QByteArray().append("JSON"))
        if jsonObject:
            jsonObject = QJsonDocument.fromJson(jsonObject).object()
            # Intent
            self.intent = jsonObject["intent"].toString()
            print("intent : " + self.intent)
            # Message
            self.message = jsonObject["message"].toString()
            # Audio
            filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
            file = QFile(filename)
            if (not file.open(QIODevice.WriteOnly)):
                print("Could not create file : " + filename)
                return
            file.write(buffer)
            print("Sound file generated at : " + filename)
            file.close()
            self.signalIndicator.emit("converse", "green")
            self.update_state.emit("converse", State.CONVERSE_NEW, {"intent": self.intent, "reply": self.message, "audiopath": filename})
        else:
            jsonObject = QJsonDocument.fromJson(buffer).object()
            if jsonObject.get("field") and jsonObject.get("value") and jsonObject.get("userId"):
                print('Converse - updateMemory responded.')
            else:
                self.signalIndicator.emit("converse", "orange")
                print('Converse - Error : Invalid response format.\n' + str(buffer))
        reply.deleteLater()

    @ehpyqtSlot(str, str, int)
    def updateMemory(self, field, value, userId):
        # Create the json request
        jsonObject = {
            'field': field,
            'value': value,
            'user_id': 'SURI{}'.format(userId)
        }
        jsonData = QJsonDocument(jsonObject)
        data = jsonData.toJson()
        request = QNetworkRequest(QUrl(self.url + '/nlp/memory'))
        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.isBusy = True
        self.networkManager.post(request, data)

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def sendRequest(self, filepath, id=None):
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

        # Id
        idPart = QHttpPart()
        idPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"user_id\""))
        idPart.setBody(QByteArray().append(str(id)))
        multiPart.append(audioPart)
        multiPart.append(textPart)
        multiPart.append(idPart)
        url = self.url+'/converse/audio'
        print(url)
        request = QNetworkRequest(QUrl(self.url+'/converse/audio'))
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

    @ehpyqtSlot('QByteArray')
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
        self.update_state.emit("converse", State.CONVERSE_NEW, {"intent": self.intent, "reply": self.message, "audiopath": filename})
        # Play the audio
        # Restart the audioplayer
        # self.play_sound.emit(filename)
