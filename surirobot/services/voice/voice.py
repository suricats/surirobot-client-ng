from PyQt5.QtCore import QThread, pyqtSignal
import logging
import time
import os
from surirobot.core.api.emotional import EmotionalAPICaller
from surirobot.core.api.exceptions import URLNotDefinedAPIException


class VoiceRecognition(QThread):
    update_state = pyqtSignal(str, int, dict)
    signal_indicator = pyqtSignal(str, str)

    send_request = pyqtSignal(str)

    NB_IMG_PER_SECOND = 0.1
    MODULE_NAME = 'voice'

    def __init__(self):
        QThread.__init__(self)

        voice_url = os.environ.get('API_EMO_URL')
        if voice_url:
            self.api_voice = EmotionalAPICaller(voice_url)
            self.api_voice.start()
        else:
            raise URLNotDefinedAPIException('Voice is not defined')
        self.send_request.connect(self.api_voice.getAnalysis)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(type(self).__name__)
        self.isBusy = False

    def __del__(self):
        self.quit()

    def run(self):
        time.sleep(5)
        voice_activated = int(os.environ.get('VOICE', '1'))
        if not voice_activated:
            self.logger.info('Voice service is deactivated.')
        while voice_activated:
            try:
                self.api_voice.getAnalysis("samples/output.wav")
            except Exception as e:
                self.logger.error('{} occurred in emotion service.\n{}'.format(type(e).__name__, e))
