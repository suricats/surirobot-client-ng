from .base import ApiCaller
from PyQt5.QtCore import pyqtSignal
from surirobot.core.common import State, ehpyqtSlot
import requests
import logging
import json


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


class VocalAPICaller(ApiCaller):

    received_reply = pyqtSignal(int, dict)
    signal_indicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)
        self.logger = logging.getLogger(type(self).__name__)

    def __del__(self):
        self.stop()

    def getAnalysis(API_Key, WavPath):

        res = requests.post("https://token.beyondverbal.com/token", data={"grant_type": "client_credentials",
                                                                          "apiKey": API_Key})
        token = res.json()['access_token']
        headers={"Authorization": "Bearer "+token}

        pp = requests.post("https://apiv4.beyondverbal.com/v4/recording/start",
                           json={"dataFormat": {"type": "WAV"}},
                           verify=False,
                           headers=headers)
        if pp.status_code != 200:
            print(pp.status_code, pp.content)
            return
        recordingId = pp.json()['recordingId']
        with open(WavPath,'rb') as wavdata:
            r = requests.post("https://apiv4.beyondverbal.com/v4/recording/"+recordingId,
                              data=wavdata,
                              verify=False,
                              headers=headers)
            return r.json()