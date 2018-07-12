from .base import ApiCaller
from .filedownloader import FileDownloader
from PyQt5.QtCore import QJsonDocument, QVariant, QFile, QIODevice, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest
import uuid
from surirobot.services import serv_ap
from surirobot.core.common import ehpyqtSlot
import os
from gtts import gTTS

class TtsApiCaller(ApiCaller):
    download = pyqtSignal(str)
    play_sound = pyqtSignal(str)
    signalIndicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

        self.local_voice = os.environ.get('LOCAL_VOICE', False)
        self.fileDownloader = FileDownloader()
        self.fileDownloader.new_file.connect(self.downloadFinished)
        self.download.connect(self.fileDownloader.sendRequest)
        self.play_sound.connect(serv_ap.play)

    def __del__(self):
        self.stop()

    @ehpyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        buffer = reply.readAll()
        if (reply.error() != QNetworkReply.NoError):
            print("TTS - Error  " + str(reply.error()))
            print("Data : " + str(buffer))
            self.signalIndicator.emit("converse", "red")
            self.networkManager.clearAccessCache()
        else:
            # Audio
            filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
            file = QFile(filename)
            if (not file.open(QIODevice.WriteOnly)):
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
        if self.local_voice:
            print('prout')
            # Play the audio directly
            audio_file = self.TMP_DIR + format(uuid.uuid4()) + ".wav"
            tts = gTTS(text=text, lang="fr", slow=False)
            tts.save(audio_file)
            print('AH BON')
            self.play_sound.emit(audio_file)
        else:
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
        if (not file.open(QIODevice.WriteOnly)):
            print("Could not create file : " + filename)
            return
        file.write(data)
        print("Sound file generated at : " + filename)
        file.close()

        # Play the audio
        self.play_sound.emit(filename)
