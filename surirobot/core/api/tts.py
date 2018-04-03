from .base import ApiCaller
from .filedownloader import FileDownloader
from PyQt5.QtCore import QJsonDocument, QVariant, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest
import uuid


class TtsApiCaller(ApiCaller):
    def __init__(self, text):
        ApiCaller.__init__(self, text)

        self.fileDownloader = FileDownloader()
        ### self.musicPlayer = MusicPlayer::getInstance();
        ### QObject::connect(fileDownloader, SIGNAL(newFile(QByteArray)), this, SLOT(downloadFinished(QByteArray)));
        ### QObject::connect(this, SIGNAL(download(QString)), fileDownloader, SLOT(sendRequest(QString)));
        ### QObject::connect(this, SIGNAL(playSound(QString)), musicPlayer, SLOT(playSound(QString)));
        ### QObject::connect(this, SIGNAL(interruptSound()), musicPlayer, SLOT(interruptRequest()));

    def __del__(self):
        self.stop()

    def receiveReply(self, reply):
        self.isBusy = False
        # audioPlayer.stop()
        if (reply.error() != QNetworkReply.NoError):
            print("Error  " + reply.error() + " : " + reply.readAll().toStdString())
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(reply.readAll()).object()
            url = jsonObject["downloadLink"].toString("")
            if (url.isEmpty()):
                self.newReply("Je ne me sens pas bien... [ERROR TTS : Fields needed don't exist.]")
            else:
                print("Downloading the sound : " + url.toStdString())
                ### emit download(url)
        reply.deleteLater()

    def sendRequest(self, text):
        self.isBusy = True
        # Json request
        jsonObject = {
            'text': text,
            'language': "fr-FR"
        }

        jsonData = QJsonDocument(jsonObject)
        data = jsonData.toJson()
        request = QNetworkRequest(self.url)

        request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
        self.networkManager.post(request, data)

    def start(self):
        ApiCaller.start()
        self.fileDownloader.start()
        self.musicPlayer.start()

    def stop(self):
        self.fileDownloader.stop()
        self.musicPlayer.currentThread.quit()
        ApiCaller.stop()

    def downloadFinished(self, data):
        print("Download finished.")
        # generate filename
        filename = self.TMP_DIR + uuid.uuid4() + ".wav"
        file = QFile(filename)
        if (not file.open(QIODevice.WriteOnly)):
            print("Could not create file : " + filename)
            return
        file.write(data)
        print("Sound file generated at : " + filename)
        file.close()

        # Play the audio
        ### emit interruptSound();
        ### emit playSound(QString::fromStdString(filename));
