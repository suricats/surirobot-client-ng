from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import time
import os
import cv2
import uuid
from surirobot.services import serv_vc
from surirobot.core.api.emotional import EmotionalAPICaller
from surirobot.core.common import Dir
from surirobot.core import ui
import face_recognition


class EmotionalRecognition(QThread):
    updateState = pyqtSignal(str, int, dict)
    signalIndicator = pyqtSignal(str, str)

    send_request = pyqtSignal(str)

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
        self.isBusy = False

        self.api_emotion.signalIndicator.connect(self.relayer)

    def __del__(self):
        self.quit()

    def run(self):
        time.sleep(5)
        while(True):
            try:
                time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
                if not self.isBusy:
                    frame = serv_vc.get_frame()
                    if frame is not None:
                        file_path = Dir.TMP + format(uuid.uuid4()) + '.jpeg'
                        cv2.imwrite(file_path, frame)
                        img = face_recognition.load_image_file(file_path)
                        encodings = True
                        # encodings = face_recognition.face_encodings(img, None, 10)
                        if encodings:
                            self.isBusy = True
                            self.send_request.emit(file_path)
            except Exception as e:
                print('Emotional - Error : ' + str(e))

    @pyqtSlot(int, dict)
    def emit_emotion_changed(self, state, data):
        self.isBusy = False
        if data.get("emotion") is not None:
            ui.setTextDown(str(data["emotion"]).upper())
        else:
            ui.setTextDown(str(data))
        self.updateState.emit(self.MODULE_NAME, state, data)

    @pyqtSlot(str, str)
    def relayer(self, a1, a2):
        self.signalIndicator.emit(a1, a2)
