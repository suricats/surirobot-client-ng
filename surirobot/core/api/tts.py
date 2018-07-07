import uuid

from PyQt5.QtCore import QJsonDocument, QVariant, QFile, QIODevice, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest

from surirobot.core.common import ehpyqtSlot
from surirobot.services import serv_ap
from .base import ApiCaller
from .filedownloader import FileDownloader


class TtsApiCaller(ApiCaller):
    download = pyqtSignal(str)
    play_sound = pyqtSignal(str)
    signalIndicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

        self.fileDownloader = FileDownloader()
        self.fileDownloader.new_file.connect(self.downloadFinished)
        self.download.connect(self.fileDownloader.sendRequest)
        self.play_sound.connect(serv_ap.play)

    def __del__(self):
        self.stop()

    @ehpyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        buffer = reply.readAll()
        if reply.error() != QNetworkReply.NoError:
            print("TTS - Error  " + str(reply.error()))
            print("Data : " + str(buffer))
            self.signalIndicator.emit("converse", "red")
            self.networkManager.clearAccessCache()
        else:
            # Audio
            filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
            file = QFile(filename)
            if not file.open(QIODevice.WriteOnly):
                print("Could not create file : " + filename)
                return
            file.write(buffer)
            print("Sound file generated at : " + filename)
            file.close()
            # Play the audio
            self.play_sound.emit(filename)
        reply.deleteLater()

    @ehpyqtSlot(str)
    def sendRequest(self, text):
        self.isBusy = True
        # Json request
        jsonObject = {
            'text': text,
            'language': "fr-FR"
        }

        jsonData = QJsonDocument(jsonObject)
        data = jsonData.toJson()

        url = QUrl(self.url+'/tts/speak')
        request = QNetworkRequest(url)

        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.networkManager.post(request, data)

    def start(self):
        ApiCaller.start(self)
        self.fileDownloader.start()

    def stop(self):
        self.fileDownloader.stop()
        ApiCaller.stop(self)

    @ehpyqtSlot('QByteArray')
    def downloadFinished(self, data):
        print("Download finished.")
        # generate filename
        filename = self.TMP_DIR + format(uuid.uuid4()) + ".wav"
        file = QFile(filename)
        if not file.open(QIODevice.WriteOnly):
            print("Could not create file : " + filename)
            return
        file.write(data)
        print("Sound file generated at : " + filename)
        file.close()

        # Play the audio
        self.play_sound.emit(filename)
