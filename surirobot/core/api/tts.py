from .base import ApiCaller
from PyQt5.QtCore import QFile, QIODevice, pyqtSignal
import uuid
from surirobot.devices import serv_ap
from surirobot.core.common import ehpyqtSlot
import os
import requests
import json
import logging
# from gtts import gTTS


class TtsApiCaller(ApiCaller):
    """
    API class for TTS API

    https://github.com/suricats/surirobot-api-converse
    """
    play_sound = pyqtSignal(str, bool)
    signal_indicator = pyqtSignal(str, str)

    def __init__(self, text):
        ApiCaller.__init__(self, text)
        self.logger = logging.getLogger(type(self).__name__)
        self.local_voice = bool(int(os.environ.get('LOCAL_VOICE', False)))
        self.play_sound.connect(serv_ap.play)

    def __del__(self):
        self.stop()

    @ehpyqtSlot(str, int)
    @ehpyqtSlot(str)
    def speak(self, text):
        """
        Transform a text into audio

        Retrieve text and send a signal to :class:`surirobot.services.audioplayer.AudioPlayer`
        'LOCAL_VOICE' environment variable influences the behaviour of this function
        Parameters
        ----------
        text : str
            Well.. the text.

        Returns
        -------
        None
            This function only send a signal
        """
        if self.local_voice:
            # Play the audio directly
            # audio_file = self.TMP_DIR + format(uuid.uuid4()) + ".wav"
            # tts = gTTS(text=text, lang="fr", slow=False)
            # tts.save(data_audio)
            # self.play_sound.emit(audio_file)
            self.play_sound.emit(text, True)
        else:
            # Json request
            data = {
                'text': text,
                'language': self.DEFAULT_LANGUAGE_EXT
            }
            data = json.dumps(data)
            r = requests.post(self.url + '/tts/speak', data=data, headers={'Content-Type': 'application/json'})
            # Receive response
            if r.status_code != 200:
                self.logger.error('HTTP {} error occurred while retrieving audio.\n{}'.format(r.status_code, r.content))
                self.signal_indicator.emit("converse", "red")
            else:
                # Audio
                filename = self.TMP_DIR + str(uuid.uuid4()) + ".wav"
                file = QFile(filename)
                if not file.open(QIODevice.WriteOnly):
                    self.logger.error("Could not create file : {}".format(filename))
                    return
                file.write(r.content)
                self.logger.info("Sound file generated at : {}".format(filename))
                file.close()
                # Play the audio
                self.play_sound.emit(filename, False)

    def start(self):
        ApiCaller.start(self)

    def stop(self):
        ApiCaller.stop(self)
