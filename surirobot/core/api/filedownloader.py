from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest

from surirobot.core.common import ehpyqtSlot
from .base import ApiCaller


class FileDownloader(ApiCaller):
    new_file = pyqtSignal('QByteArray')

    def __init__(self):
        ApiCaller.__init__(self)
        self.isBusy = False

    def __del__(self):
        self.stop()

    @ehpyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        data = reply.readAll()
        self.new_file.emit(data)
        reply.deleteLater()

    @ehpyqtSlot(str)
    def sendRequest(self, urlStr):
        url = QUrl.fromUserInput(urlStr)
        parsedUrl = QUrl(url)
        request = QNetworkRequest(parsedUrl)
        self.networkManager.get(request)
