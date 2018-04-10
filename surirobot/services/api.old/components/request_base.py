import abc
import logging
from PyQt5.QtCore import QObject
from PyQt5.QtNetwork import QNetworkAccessManager


class BaseRequest(QObject):
    def __init__(self, url='https://www.google.fr'):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.url = url
        self.networkManager = QNetworkAccessManager(self)
        self.networkManager.finished.connect(self.receive_reply)

    @abc.abstractmethod
    def receive_reply(self, reply):
        pass
