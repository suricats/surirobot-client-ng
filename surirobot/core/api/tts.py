from .base import ApiCaller
from .filedownloader import FileDownloader
from PyQt5.QtCore import QJsonDocument, QVariant, QFile, QIODevice, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest
import uuid
from surirobot.services import serv_ap


class TtsApiCaller(ApiCaller):
    download = pyqtSignal(str)
    play_sound = pyqtSignal(str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

        self.fileDownloader = FileDownloader()
        self.fileDownloader.new_file.connect(self.downloadFinished)
        self.download.connect(self.fileDownloader.sendRequest)
        self.play_sound.connect(serv_ap.play)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        if (reply.error() != QNetworkReply.NoError):
            print("TTS - Error  " + str(reply.error()))
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(reply.readAll()).object()
            url = jsonObject["downloadLink"].toString("")
            if (not url):
                print('TTS - Error : No url')
                # self.new_reply.emit("Je ne me sens pas bien... [ERROR TTS : Fields needed don't exist.]")
            else:
                print("Downloading the sound : " + url)
                self.download.emit(url)
        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, text):
        self.isBusy = True
        # Json request
        jsonObject = {
            'text': text,
            'language': "fr-FR"
        }

        jsonData = QJsonDocument(jsonObject)
        data = jsonData.toJson()
        request = QNetworkRequest(QUrl(self.url))

        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.networkManager.post(request, data)

    def start(self):
        ApiCaller.start(self)
        self.fileDownloader.start()

    def stop(self):
        self.fileDownloader.stop()
        ApiCaller.stop(self)

    @pyqtSlot('QByteArray')
    def downloadFinished(self, data):
        print("Download finished.")
        # generate filename
        filename = self.TMP_DIR + format(uuid.uuid4()) + ".wav"
        file = QFile(filename)
        if (not file.open(QIODevice.WriteOnly)):
            print("Could not create file : " + filename)
            return
        file.write(data)
        print("Sound file generated at : " + filename)
        file.close()

        # Play the audio
        self.play_sound.emit(filename)
