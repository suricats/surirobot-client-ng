from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkReply, QHttpMultiPart, QHttpPart, QNetworkRequest
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QJsonDocument, QUrl, QVariant, QFile, QIODevice, QByteArray
from surirobot.core.common import State, ehpyqtSlot
import requests
import logging


class EmotionalAPICaller(ApiCaller):
    received_reply = pyqtSignal(int, dict)
    signal_indicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str)
    def analyse(self, file_path):
        with open(file_path, 'rb') as file:
            r = requests.post(self.url + '/microsoft/analyse', data=file.read(), headers={'Content-Type': 'image/jpeg'})
            if r.status_code != 200:
                self.logger.error('HTTP {} error occurred.'.format(r.status_code))
                self.signal_indicator.emit("emotion", "red")
            else:
                json_object = r.json()
                emotion = json_object["emotion"]
                # percent = jsonObject["percent"]
                if emotion:
                    self.received_reply.emit(
                        State.EMOTION_NEW, {'emotion': emotion}
                    )
                else:
                    self.received_reply.emit(
                        State.EMOTION_NO, {'emotion': []}
                    )
                self.signal_indicator.emit("emotion", "green")
