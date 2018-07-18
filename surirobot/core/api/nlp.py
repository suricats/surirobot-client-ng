import json

from .base import ApiCaller
from PyQt5.QtCore import pyqtSignal
from surirobot.core.common import State, ehpyqtSlot
import requests
import logging


class NlpApiCaller(ApiCaller):
    """
    API class for NLP API

    https://github.com/suricats/surirobot-api-converse
    """
    update_state = pyqtSignal(str, int, dict)
    signal_indicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str, str, int)
    def memory(self, field, value, user_id):
        """
        Update the memory of a conversation.

        Update a specific field in the memory of a conversation
        Parameters
        ----------
        field : str
            field that need to be updated
        value : str
            new value of the field
        user_id : str
            ID of the conversation

        Returns
        -------
        None
            This function only display the result
        """
        # Create the json request
        data = {
            'field': field,
            'value': value,
            'user_id': 'SURI{}'.format(user_id)
        }
        data = json.dumps(data)
        r = requests.post(self.url + '/nlp/memory', data=data, headers={'Content-Type': 'application/json'})
        # Receive response
        if r.status_code != 200:
            self.logger.error('HTTP {} error occurred while updating memory.'.format(r.status_code))
            print(r.content)
            self.signal_indicator.emit("converse", "orange")
        else:
            self.logger.info('Memory updated successfully.')

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def answer(self, text, user_id=None):
        """
        Give the NLP answer of a text

        Take a text and analyze it to give a signal that contains state, intent and reply
        Parameters
        ----------
        text : str
            The input text. Isn't that obvious ?
        user_id : str
            ID of the conversation

        Returns
        -------
        None
            This function send a signal
        """
        # Create the json request
        data = {
            'text': text,
            'language': self.DEFAULT_LANGUAGE,

        }
        if user_id:
            data['user_id'] = user_id
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
    def intent(self, text, user_id=None):
        """
        Give the intent of a text

        Take a text and analyze it to give a signal that contains state, intent and reply
        Parameters
        ----------
        text : str
            The input text. Isn't that obvious ?
        user_id : str
            ID of the conversation

        Returns
        -------
        None
            This function send a signal
        """
        # Create the json request
        data = {
            'text': text,
            'language': self.DEFAULT_LANGUAGE,

        }
        if id:
            data['user_id'] = user_id
        r = requests.post(self.url + '/nlp/intent', data=data)
        # Receive response
        if r.status_code != 200:
            self.logger.error('HTTP {} error occurred while retrieving intent answer.'.format(r.status_code))
            print(r.content)
            self.signal_indicator.emit("converse", "orange")
        else:
            json_object = r.json()
            intent = json_object["intents"][0]["slug"]
            self.update_state.emit("converse", State.CONVERSE_NEW, {"intent": intent, "reply": "?"})
