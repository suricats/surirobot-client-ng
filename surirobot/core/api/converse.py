from .base import ApiCaller
from PyQt5.QtCore import QFile, QIODevice, pyqtSignal
import uuid
from surirobot.services import serv_ap
from surirobot.core.common import State, Dir, ehpyqtSlot
import os
import json
# from gtts import gTTS
import requests
import logging


class ConverseApiCaller(ApiCaller):
    """
    API class for Converse API

    https://github.com/suricats/surirobot-api-converse
    """
    play_sound = pyqtSignal(str)
    update_state = pyqtSignal(str, int, dict)
    signal_indicator = pyqtSignal(str, str)

    def __init__(self, url):
        ApiCaller.__init__(self, url)
        self.local_voice = os.environ.get('LOCAL_VOICE', False)
        self.play_sound.connect(serv_ap.play)
        self.logger = logging.getLogger(__name__)

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
                url = self.url+'/converse/text'
            else:
                url = self.url+'/converse/audio'
            data = {'language': self.DEFAULT_LANGUAGE_EXT}
            if user_id:
                data['id'] = user_id
            self.logger.info("Sent to Converse API : File - {} : {}Ko".format(file_path, os.fstat(file.fileno()).st_size / 1000))
            r = requests.post(url, files={'audio': file}, data=data)
            # Receive response
            if r.status_code != 200:
                self.logger.error('HTTP {} error occurred.'.format(r.status_code))
                self.signal_indicator.emit("converse", "red")
                message = "Oh mince ! Je ne fonctionne plus très bien :("
                filename = Dir.DATA + "error.wav"
                self.update_state.emit("converse", State.CONVERSE_NEW,
                                       {"intent": "error", "reply": message, "audiopath": filename})
            else:
                # Text response
                if self.local_voice:
                    json_object = r.json()
                    print(json_object)
                    intent = json_object.get('intent', 'no-understand')
                    message = json_object.get('message', '.')
                    self.signal_indicator.emit("converse", "green")
                    self.update_state.emit("converse", State.CONVERSE_NEW,
                                           {"intent": intent, "reply": message, "audiopath": message})
                # Audio response
                else:
                    json_header = json.loads(r.headers['JSON'])
                    # Intent
                    intent = json_header["intent"]
                    print("intent : " + intent)
                    # Message
                    message = json_header["message"]
                    # Audio
                    filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
                    file = QFile(filename)
                    if not file.open(QIODevice.WriteOnly):
                        print("Could not create file : " + filename)
                        return
                    file.write(r.content)
                    print("Sound file generated at : " + filename)
                    file.close()
                    self.signal_indicator.emit("converse", "green")
                    self.update_state.emit("converse", State.CONVERSE_NEW,
                                           {"intent": intent, "reply": message, "audiopath": filename})

    def start(self):
        self.converse_audio()
        ApiCaller.start(self)

    def stop(self):
        super().stop()
