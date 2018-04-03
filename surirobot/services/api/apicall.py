import abc
import logging
from PyQt5.QtCore import QThread
from PyQt5.QtNetwork import QNetworkAccessManager


class ApiCaller(QThread):
    def __init__(self, url='https://www.google.fr'):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.url = url
        self.networkManager = QNetworkAccessManager(self)
        self.networkManager.finished.connect(self.receive_reply)

    def __del__(self):
        self.wait()

    @abc.abstractmethod
    def receive_reply(self, reply):
        pass
