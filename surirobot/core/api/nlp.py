from .base import ApiCaller
from PyQt5.QtCore import QJsonDocument, QVariant
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest


class NlpApiCaller(ApiCaller):
    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

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
                    ### emit newReply(message)
            else:
                ### emit newReply(QString("Can't find message."));
                pass
        reply.deleteLater()

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
