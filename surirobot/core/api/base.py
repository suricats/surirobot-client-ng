from PyQt5.QtCore import QObject, QThread
from PyQt5.QtNetwork import QNetworkAccessManager


class ApiCaller(QObject):
    TMP_DIR = 'tmp/'
    DEFAULT_LANGUAGE = 'fr'

    def __init__(self, url='https://www.google.fr'):
        self.url = url
        self.networkManager = QNetworkAccessManager(self)
        ### QObject.connect(networkManager, SIGNAL(finished(QNetworkReply*)), this, SLOT(receiveReply(QNetworkReply*)));
        self.currentThread = QThread()
        self.moveToThread(self.currentThread)

    def __del__(self):
        self.currentThread.quit()

    def start(self):
        self.currentThread.start()

    def stop(self):
        self.currentThread.quit()
