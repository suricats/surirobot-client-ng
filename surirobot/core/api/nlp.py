from .base import ApiCaller
from PyQt5.QtCore import QJsonDocument, QVariant, pyqtSlot, pyqtSignal
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest


class NlpApiCaller(ApiCaller):
    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        if (reply.error() != QNetworkReply.NoError):
            print("Error  " + reply.error() + " : " + reply.readAll().toStdString())
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(reply.readAll()).object()
            print("Received from Converse API : " + reply.readAll().toStdString())
            messagesJson = jsonObject["results"].toObject()["messages"].toArray()
            if (not messagesJson.isEmpty()):
                queryValue = messagesJson[0].toObject()["content"]
                if ((not queryValue.isNull()) and (not queryValue.isUndefined())):
                    message = queryValue.toString()
                    self.new_reply.emit(message)
            else:
                self.new_reply.emit("Can't find message.")
        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, text):
        if (text != ""):
            # Create the json request
            jsonObject = {
                'text': text,
                'language': self.DEFAULT_LANGUAGE
            }

            jsonData = QJsonDocument(jsonObject)
            data = jsonData.toJson()
            request = QNetworkRequest(self.url)
            print("Sended to NLP API : " + data.toStdString())
            # request.setAttribute(QNetworkRequest::FollowRedirectsAttribute, True);
            request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"));
            self.isBusy = True
            self.networkManager.post(request, data)
