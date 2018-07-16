from .base import ApiCaller
from PyQt5.QtCore import pyqtSignal
from surirobot.core.common import State, ehpyqtSlot
import requests
import logging


class NlpApiCaller(ApiCaller):

    update_state = pyqtSignal(str, int, dict)

    def __init__(self, text):
        ApiCaller.__init__(self, text)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str, str, int)
    def memory(self, field, value, user_id):
        # Create the json request
        data = {
            'field': field,
            'value': value,
            'user_id': 'SURI{}'.format(user_id)
        }
        r = requests.post(self.url + '/nlp/memory', data=data)
        # Receive response
        if r.status_code != 200:
            self.logger.error('HTTP {} error occurred while updating memory.'.format(r.status_code))
            print(r.content)
            self.signal_indicator.emit("converse", "orange")
        else:
            self.logger.info('Memory updated successfully.')

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def answer(self, text, id=None):
        # Create the json request
        data = {
            'text': text,
            'language': self.DEFAULT_LANGUAGE,

        }
        if id:
            data['user_id'] = id
        r = requests.post(self.url + '/nlp/answer', data=data)
        # Receive response
        if r.status_code != 200:
            self.logger.error('HTTP {} error occurred while retrieving nlp answer.'.format(r.status_code))
            print(r.content)
            self.signal_indicator.emit("converse", "orange")
        else:
            json_object = r.json()
            message = json_object["messages"][0]["content"]
            intent = json_object["nlp"]["intents"][0]["slug"]
            self.update_state.emit("converse", State.CONVERSE_NEW,
                                   {"intent": intent, "reply": message})

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def intent(self, text, id=None):
        # Create the json request
        data = {
            'text': text,
            'language': self.DEFAULT_LANGUAGE,

        }
        if id:
            data['user_id'] = id
        r = requests.post(self.url + '/nlp/intent', data=data)
        # Receive response
        if r.status_code != 200:
            self.logger.error('HTTP {} error occurred while retrieving intent answer.'.format(r.status_code))
            print(r.content)
            self.signal_indicator.emit("converse", "orange")
        else:
            json_object = r.json()
            message = json_object["messages"][0]["content"]
            intent = json_object["nlp"]["intents"][0]["slug"]
            self.update_state.emit("converse", State.CONVERSE_NEW,
                                   {"intent": intent, "reply": message})
