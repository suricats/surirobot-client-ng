from .base import ApiCaller
from PyQt5.QtCore import pyqtSignal
from surirobot.core.common import State, ehpyqtSlot
import requests
import logging
import os


class SttApiCaller(ApiCaller):
    """
    API class for STT API

    https://github.com/suricats/surirobot-api-converse
    """
    update_state = pyqtSignal(str, int, dict)

    def __init__(self, url):
        ApiCaller.__init__(self, url)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str)
    def recognize(self, file_path):
        """
        Recognize an audio file and give the corresponding text.

        Retrieve path of audio file and send a signal that includes state, intent("@STT") and reply

        Parameters
        ----------
        file_path : str
            path of audio file

        Returns
        -------
        None
            This function only send a signal
        """
        with open(file_path, 'rb') as file:
            # Send request
            url = self.url+'/stt/recognize'
            data = {'language': self.DEFAULT_LANGUAGE_EXT}
            if id:
                data['id'] = id
            self.logger.info("Sent to STT API : File - {} : {}Ko".format(file_path, os.fstat(file.fileno()).st_size / 1000))
            r = requests.post(url, files={'audio': file}, data=data)
            # Receive response
            if r.status_code != 200:
                self.logger.error('HTTP {} error occurred while retrieving text.'.format(r.status_code))
                print(r.content)
                # self.signal_indicator.emit("converse", "orange")
                # self.update_state.emit("converse", State.CONVERSE_NEW, {"intent": "dont-understand", "reply": "Je n'ai pas compris."})
            else:
                json_object = r.json()
                self.update_state.emit("converse", State.CONVERSE_NEW,
                                       {"intent": "@STT", "reply": json_object["text"]})
