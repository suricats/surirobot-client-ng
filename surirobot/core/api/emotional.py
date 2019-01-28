from .base import ApiCaller
from PyQt5.QtCore import pyqtSignal
from surirobot.core.common import State, ehpyqtSlot
import requests
import logging
import json
from ffmpy import FFmpeg
import os


class EmotionalAPICaller(ApiCaller):
    """
    API class for Emotional API

    https://github.com/suricats/surirobot-api-emotions
    """
    received_reply = pyqtSignal(int, dict)
    signal_indicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)
        self.logger = logging.getLogger(type(self).__name__)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str)
    def analyse(self, file_path):
        """
        Send image to Converse API that will analyze it to give the main emotion.

        Retrieve path of image file and send a signal that includes state and emotion

        Parameters
        ----------
        file_path : str
            path of image file

        Returns
        -------
        None
            This function only send a signal
        """
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

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def getAnalysis(self, file_path, user_id=None):
        new_file = file_path.split('.')[0] + '-format.wav'
        ff = FFmpeg(
            inputs={file_path: None},
            outputs={new_file: '-acodec pcm_s16le -ac 1 -ar 8000'}
        )
        ff.run()
        with open(new_file, 'rb') as wavdata:
            r = requests.post(self.url + '/beyond_verbal/analyse', data=wavdata, headers={'Content-Type': 'audio/x-wav'})
        if r.status_code != 200:
            self.logger.error('HTTP {} error occurred.'.format(r.status_code))
            self.signal_indicator.emit("emotion", "red")
        else :
            self.signal_indicator.emit("emotion", "green")
    
            print (json.dumps(r.json(), indent=4, sort_keys=True))
            return r.json()

        #data = getAnalysis(BEYONDVERBAL_API_CREDENTIAL, "samples/output.wav")
        #print(json.dumps(data, sort_keys=True, indent=4))

    def start(self):
        ApiCaller.start(self)