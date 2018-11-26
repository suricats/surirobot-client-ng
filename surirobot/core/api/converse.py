import json
import logging
import os
import uuid

# from gtts import gTTS
import requests
from PyQt5.QtCore import QFile, QIODevice, pyqtSignal

from surirobot.core.common import State, Dir, ehpyqtSlot
from .base import ApiCaller
from surirobot.core import ui


class ConverseApiCaller(ApiCaller):
    """
    API class for Converse API

    https://github.com/suricats/surirobot-api-converse
    """
    update_state = pyqtSignal(str, int, dict)
    signal_indicator = pyqtSignal(str, str)
    signal_ui_input_text = pyqtSignal(str)

    def __init__(self, url):
        ApiCaller.__init__(self, url)
        self.signal_ui_input_text.connect(ui.set_text_input)
        self.local_voice = bool(int(os.environ.get('LOCAL_VOICE', '0')))
        self.logger = logging.getLogger(type(self).__name__)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def converse_audio(self, file_path, user_id=None):
        """
        Send audio to Converse API and retrieve a audio or text response.

        Retrieve path of audio file and send a signal that includes state, nlp reply and audio file path

        Parameters
        ----------
        file_path : str
            path of audio file
        user_id : str
            id of the conversation

        Returns
        -------
        None
            This function only send a signal
        """
        with open(file_path, 'rb') as file:
            # Send request
            if self.local_voice:
                url = self.url + '/converse/text'
            else:
                url = self.url + '/converse/audio'
            data = {'language': self.DEFAULT_LANGUAGE_EXT}
            if user_id:
                data['user_id'] = 'SURI{}'.format(user_id)
            self.logger.info(
                "Sent to Converse API : File - {} : {}Ko".format(file_path, os.fstat(file.fileno()).st_size / 1000))
            r = requests.post(url, files={'audio': file}, data=data)
            # Receive response
            if r.status_code != 200:
                self.logger.error('HTTP {} error occurred.'.format(r.status_code))
                self.logger.error(r.content)
                self.signal_indicator.emit("converse", "red")
                message = "Oh mince ! Je ne fonctionne plus très bien :("
                filename = Dir.DATA + "error.wav"
                if self.local_voice:
                    self.update_state.emit("converse", State.CONVERSE_NEW,
                                           {"intent": "error", "reply": message, "local": True})

                else:
                    self.update_state.emit("converse", State.CONVERSE_NEW,
                                           {"intent": "error", "reply": message, "audiopath": filename})
            else:
                # Text response
                if self.local_voice:
                    json_object = r.json()
                    self.logger.info('Full converse response :\n{}'.format(json_object))
                    self.signal_ui_input_text.emit(json_object.get('input'))
                    intent = json_object.get('intent', 'no-understand')
                    message = json_object.get('message', '.')
                    self.signal_indicator.emit("converse", "green")
                    self.update_state.emit("converse", State.CONVERSE_NEW,
                                           {"intent": intent, "reply": message, "local": True})
                # Audio response
                else:
                    json_header = json.loads(r.headers['JSON'])
                    self.signal_ui_input_text.emit(json_header.get('input'))
                    # Intent
                    intent = json_header["intent"]
                    #intent='show-picture'
                    self.logger.info("Intent detected : {}".format(intent))
                    # Message
                    message = json_header["message"]
                    # Audio
                    filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
                    file = QFile(filename)
                    if not file.open(QIODevice.WriteOnly):
                        self.logger.error("Could not create file : {}".format(filename))
                        return
                    file.write(r.content)
                    self.logger.info("Sound file generated at : {}".format(filename))
                    file.close()
                    self.signal_indicator.emit("converse", "green")
                    self.update_state.emit("converse", State.CONVERSE_NEW,
                                           {"intent": intent, "reply": message, "audiopath": filename})

    def start(self):
        ApiCaller.start(self)

    def stop(self):
        super().stop()
