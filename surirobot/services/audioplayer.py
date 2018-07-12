from PyQt5.QtCore import QThread, pyqtSlot
import logging
import simpleaudio as sa
import subprocess
import platform
from surirobot.core.common import ehpyqtSlot
import os
# Local TTS engine
# import pyttsx3
# import asyncio


class AudioPlayer(QThread):
    def __init__(self):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.playObj = None

        self.local_voice = os.environ.get('LOCAL_VOICE', False)
        # self.engine = pyttsx3.init(driverName='espeak')
        # self.engine.setProperty('rate', 150)
        # self.engine.setProperty('voice', 'french')  # changes the voice

    def __del__(self):
        self.stop()
        self.quit()

    @ehpyqtSlot()
    def stop(self):
        if self.playObj:
            self.playObj.stop()
            self.logger.info('Stop playing.')

    @ehpyqtSlot(str)
    def play(self, filename):
        print('salut')
        print(filename)
        try:
            if platform.system() == "Darwin":
                print('Audio is desactivated in MAC OS')
            else:
                self.stop()
                waveObj = sa.WaveObject.from_wave_file(filename)
                self.logger.info('Now playing' + str(filename) + '.')
                self.playObj = waveObj.play()
        except Exception as e:
            self.logger.info('Error : ' + str(e))

