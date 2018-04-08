from .request_base import BaseRequest
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot


class FileDownloader(BaseRequest):
    new_file = pyqtSignal('QByteArray')

    def __init__(self):
        BaseRequest.__init__(self)

    @pyqtSlot('QNetworkReply')
    def receiveReply(self, reply):
        self.isBusy = False
        data = reply.readAll()
        self.new_file.emit(data)
        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, urlStr):
        url = QUrl.fromUserInput(urlStr)
        parsedUrl = QUrl(url)
        request = QNetworkRequest(parsedUrl)
        self.networkManager.get(request)
