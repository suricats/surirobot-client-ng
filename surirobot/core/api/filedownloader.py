from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl


class FileDownloader(ApiCaller):
    def __init__(self):
        ApiCaller.__init__(self)

    def __del__(self):
        self.stop()

    def receiveReply(self, reply):
        self.isBusy = False
        data = reply.readAll()
        ### emit newFile(data)
        reply.deleteLater()

    def sendRequest(self, urlStr):
        url = QUrl.fromUserInput(urlStr)
        parsedUrl = QUrl(url)
        request = QNetworkRequest(parsedUrl)
        self.networkManager.get(request)
