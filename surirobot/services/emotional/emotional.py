from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import time
import os
import cv2
import base64
from surirobot.services import serv_vc
from surirobot.core.api.emotional import EmotionalAPICaller


class EmotionalRecognition(QThread):
    updateState = pyqtSignal(str, int, dict)

    send_request = pyqtSignal(bytes)

    NB_IMG_PER_SECOND = 0.1
    MODULE_NAME = 'emotion'

    def __init__(self):
        QThread.__init__(self)

        self.api_emotion = EmotionalAPICaller(os.environ.get('API_EMO_URL'))
        self.api_emotion.start()

        self.send_request.connect(self.api_emotion.sendRequest)
        self.api_emotion.received_reply.connect(self.emit_emotion_changed)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.wait()

    def run(self):
        time.sleep(5)

        while(True):
            time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
            frame = serv_vc.get_frame()
            retval, buffer = cv2.imencode('.jpeg', frame)
            image_base64 = base64.b64encode(buffer)
            self.send_request.emit(image_base64)

    @pyqtSlot(int, dict)
    def emit_emotion_changed(self, state, data):
        self.updateState.emit(self.MODULE_NAME, state, data)
