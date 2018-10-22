from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import time
import os
import cv2
import uuid
from surirobot.devices import serv_vc
from surirobot.core.api.emotional import EmotionalAPICaller
from surirobot.core.api.emotional import VocalAPICaller
from surirobot.core.api.exceptions import URLNotDefinedAPIException
from surirobot.core.common import Dir, ehpyqtSlot
from surirobot.core import ui
import face_recognition


class EmotionalRecognition(QThread):
    update_state = pyqtSignal(str, int, dict)
    signal_indicator = pyqtSignal(str, str)

    send_request = pyqtSignal(str)

    NB_IMG_PER_SECOND = 0.1
    MODULE_NAME = 'emotion'

    def __init__(self):
        QThread.__init__(self)

        emo_url = os.environ.get('API_EMO_URL')
        if emo_url:
            self.api_emotion = EmotionalAPICaller(emo_url)
            self.api_emotion.start()
        else:
            raise URLNotDefinedAPIException('Emotion')
        self.send_request.connect(self.api_emotion.analyse)
        self.api_emotion.received_reply.connect(self.emit_emotion_changed)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(type(self).__name__)
        self.isBusy = False

        self.api_emotion.signal_indicator.connect(self.relayer)

    def __del__(self):
        self.quit()

    def run(self):
        time.sleep(5)
        emo_activated = int(os.environ.get('EMO', '1'))
        if not emo_activated:
            self.logger.info('Emotion service is deactivated.')
        while emo_activated:
            try:
                time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
                if not self.isBusy:
                    frame = serv_vc.get_frame()
                    if frame is not None:
                        file_path = Dir.TMP + format(uuid.uuid4()) + '.jpeg'
                        cv2.imwrite(file_path, frame)
                        img = face_recognition.load_image_file(file_path)
                        encodings = face_recognition.face_encodings(img, None, 10)
                        if encodings:
                            self.isBusy = True
                            self.send_request.emit(file_path)
                        else:
                            ui.set_text_down("NO FACE")
            except Exception as e:
                self.logger.error('{} occurred in emotion service.\n{}'.format(type(e).__name__, e))

    @ehpyqtSlot(int, dict)
    def emit_emotion_changed(self, state, data):
        self.isBusy = False
        if data.get("emotion") is not None:
            ui.set_text_down(str(data["emotion"]).upper())
        else:
            ui.set_text_down(str(data))
        self.update_state.emit(self.MODULE_NAME, state, data)

    @ehpyqtSlot(str, str)
    def relayer(self, a1, a2):
        self.signal_indicator.emit(a1, a2)
