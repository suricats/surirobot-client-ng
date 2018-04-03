from .base import ApiCaller
from PyQt5.QtCore import QByteArray, QJsonDocument, QVariant, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest
import uuid


class ConverseApiCaller(ApiCaller):
    def __init__(self, url='https://www.google.fr'):
        ApiCaller.__init__(self, url)

        self.intentMode = False
        ### fileDownloader = new FileDownloader();
        ### musicPlayer = MusicPlayer::getInstance();
        ### QObject::connect(fileDownloader, SIGNAL(newFile(QByteArray)), this, SLOT(downloadFinished(QByteArray)));
        ### QObject::connect(this, SIGNAL(download(QString)), fileDownloader, SLOT(sendRequest(QString)));
        ### QObject::connect(this, SIGNAL(playSound(QString)), musicPlayer, SLOT(playSound(QString)));
        ### QObject::connect(this, SIGNAL(interruptSound()), musicPlayer, SLOT(interruptRequest()));

    def __del__(self):
        self.stop()

    def receiveReply(self, reply):
        self.isBusy = False
        buffer = QByteArray(reply.readAll())
        if (reply.error() != QNetworkReply.NoError):
            print("Error  " + reply.error() + " : " + buffer.toStdString())
            self.networkManager.clearAccessCache()
        jsonObject = QJsonDocument.fromJson(buffer).object()
        if self.intentMode:
            intent = jsonObject["intent"].toString()
            if (intent == "say-yes"):
                print("OUI INTENT")
                ### emit newIntent(State::STATE_CONFIRMATION_YES, intent.toUtf8())
            if (intent == "say-no"):
                print("OUI INTENT")
                ### emit newIntent(State::STATE_CONFIRMATION_NO, intent.toUtf8())
        else:
            message = jsonObject["answerText"].toString()
            url = jsonObject["answerAudioLink"].toString()
            if (not message.isEmpty()):
                print("Received from Converse API : " + message.toStdString())
                ### emit newReply(message);
                pass
            else:
                ### emit newReply("Je ne me sens pas bien... [ERROR Conv : Field message needed but doesn't exist.]");
                pass
            if(not url.isEmpty()):
                print("Downloading the sound : " + url.toStdString())
                ### emit download(url)

        reply.deleteLater()

    def sendRequest(self, filepath):
        multiPart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        # Language
        textPart = QHttpPart()
        textPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"language\""))
        textPart.setBody(DEFAULT_LANGUAGE)
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
        textPart.setHeader(QNetworkRequest.ContentDispositionHeader, QVariant("form-data; name=\"userId\""))
        textPart.setBody("1")
        multiPart.append(audioPart)
        multiPart.append(textPart)
        multiPart.append(idPart)
        request = QNetworkRequest(self.url)
        print("Sended to Converse API : " + "File - " + file.fileName().toStdString() + " - " + str(file.size() / 1000) + "Ko")
        self.isBusy = True
        reply = self.networkManager.post(request, multiPart)
        multiPart.setParent(reply)

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
        ### emit interruptSound()
        ### emit playSound(filename)
