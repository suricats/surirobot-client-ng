from .base import ApiCaller
from PyQt5.QtCore import QJsonDocument, QVariant, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkReply, QNetworkRequest
from surirobot.core.common import State


class NlpApiCaller(ApiCaller):

    updateState = pyqtSignal(str, int, dict)

    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        buffer = reply.readAll()
        if (reply.error() != QNetworkReply.NoError):
            print("NLP - Error  " + str(reply.error()) + " : " + buffer.data().decode('utf8'))
            self.networkManager.clearAccessCache()
        else:
            jsonObject = QJsonDocument.fromJson(buffer).object()
            # print("Received from NLP API : " + str(buffer))
            # getAnswer reply
            if jsonObject["results"] and jsonObject["message"]:
                self.message = jsonObject["results"]["messages"][0]["content"]
                intents = jsonObject["results"]["conversation"]["intents"]
                if intents:
                    self.intent = intents[0]["slugs"]
                else:
                    self.intent = "dont-understood"
                self.updateState.emit("converse", State.STATE_CONVERSE_NEW, {"intent": self.intent.toString(), "reply": self.message.toString()})
            else:
                self.new_reply.emit("Can't find message.")
        reply.deleteLater()

    @pyqtSlot(str, int)
    def sendRequest(self, text, id=None):
        if (text != ""):
            # Create the json request
            jsonObject = {
                'text': text,
                'language': self.DEFAULT_LANGUAGE
            }
            if id:
                jsonObject['conversation_id'] = id
            print('jsonObject : ' + str(jsonObject))
            jsonData = QJsonDocument(jsonObject)
            data = jsonData.toJson()
            request = QNetworkRequest(QUrl(self.url))
            # print("Sended to NLP API : " + str(data))
            # request.setAttribute(QNetworkRequest::FollowRedirectsAttribute, True);
            request.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("application/json"))
            self.isBusy = True
            self.networkManager.post(request, data)
