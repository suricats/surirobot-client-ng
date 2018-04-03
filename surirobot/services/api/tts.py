from .apicall import ApiCaller
from .downloader import FileDownloader
import os
import uuid
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QFile, QIODevice, QJsonDocument
from PyQt5.QtNetwork import QNetworkReply
from surirobot.core import ui, serv_ap


class TtsApi(ApiCaller):
    download = pyqtSignal(str)
    no_voice = pyqtSignal(str)

    def __init__(self):
        ApiCaller.__init__(self, os.environ.get('API_TTS_URL'))

        self.file_downloader = FileDownloader()

        self.download.connect(self.file_downloader.sendRequest)
        self.file_downloader.new_file.connect(self.download_finished)
        self.no_voice.connect(ui.setTextUp)

    def __del__(self):
        self.wait()

    def run(self):
        pass

    def receive_reply(self, reply):
        self.isBusy = False
        if (reply.error() != QNetworkReply.NoError):
            print("Error  " + reply.error() + " : " + reply.readAll())
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument(reply.readAll())
            url = jsonObject["downloadLink"]
            if (not url):
                self.no_voice.emit("Je ne me sens pas bien... [ERROR TTS : Fields needed don't exist.]")
            else:
                self.logger.info("Downloading the sound : " + url)
                self.download.emit(url)
        reply.deleteLater()

    @pyqtSlot('QByteArray')
    def download_finished(self, data):
        self.logger.info("Download finished.")

        filename = os.environ.get('TMP_DIR') + uuid.uuid4() + ".wav"
        file = QFile(filename)
        if (not file.open(QIODevice.WriteOnly)):
            self.logger.error("Could not create file : " + filename)
            return

        file.write(data)
        self.logger.info("Sound file generated at : " + filename)
        file.close()

        # Play the audio
        serv_ap.play(filename)
