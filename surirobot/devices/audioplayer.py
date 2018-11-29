import logging
import os
import io
import platform

# Local TTS engine
import pyttsx3
import simpleaudio as sa
from PyQt5.QtCore import QThread, QObject

from surirobot.core.common import ehpyqtSlot


class AudioPlayer(QObject):
    """
    Threaded service that play audio
    """
    playObj = ...  # type: sa.WaveObject

    def __init__(self):
        QObject.__init__(self)
        self.currentThread = QThread()
        self.moveToThread(self.currentThread)

        self.logger = logging.getLogger(type(self).__name__)
        self.playObj = None

        self.local_voice = bool(int(os.environ.get('LOCAL_VOICE', False)))
        self.engine = pyttsx3.init(driverName='espeak')
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('voice', 'french')  # changes the voice

    def __del__(self):
        try:
            self.stop()
            self.currentThread.quit()
        except Exception as e:
            print(e)
            print('Stopping audio player.')

    def start(self, priority=None):
        """
        Start the thread of the API caller
        """
        self.currentThread.start(priority)

    @ehpyqtSlot()
    def stop(self):
        if self.playObj:
            self.playObj.stop()
            # self.logger.info('Stop playing.')

    @ehpyqtSlot(str, bool)
    @ehpyqtSlot(str)
    def play(self, data, local=False):
        # Case: We use local engine to transform text into voice and play it
        if local:
            self.engine.say(data)
            self.engine.runAndWait()
        else:
            try:
                self.stop()
                try:
                    file_b = io.BytesIO(open(data, 'rb').read())
                except:
                    self.logger.error("Can't read file : ".format(data))
                    raise Exception("Can't read file : ".format(data))
                wave_obj = sa.WaveObject.from_wave_file(file_b)
                print(wave_obj)
                self.logger.info('Now playing {}.'.format(data))
                self.playObj = wave_obj.play()
            except Exception as e:
                self.logger.error('{} occurred while playing audio\n{}'.format(type(e).__name__, e))
