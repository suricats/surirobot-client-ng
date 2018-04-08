import os
import uuid
import logging
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QFile, QIODevice, QJsonDocument, QObject
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest, QVariant, QNetworkAccessManager
from surirobot.core import ui, serv_ap


class TtsApi(QObject):
    download = pyqtSignal(str)
    no_voice = pyqtSignal(str)

    def __init__(self, to_say):
        self.to_say = to_say

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.url = os.environ.get('API_TTS_URL')
        self.networkManager = QNetworkAccessManager(self)

        self.networkManager.finished.connect(self.receive_reply)

    @pyqtSlot()
    def sendRequest(self):
        self.isBusy = True
        json = {
            'text': self.to_say,
            'language': 'fr-FR'
        }

        jsonDocument = QJsonDocument(json)
        request = QNetworkRequest(self.url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.networkManager.post(request, jsonDocument.toJson)

    @pyqtSlot('QNetworkReply')
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
