from PyQt5.QtCore import QThread, pyqtSlot
import logging
import simpleaudio as sa


class AudioPlayer(QThread):
    def __init__(self):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.playObj = None

    def __del__(self):
        self.stop()
        self.quit()

    @pyqtSlot()
    def stop(self):
        if self.playObj:
            self.playObj.stop()
            self.logger.info('Stop playing.')

    @pyqtSlot(str)
    def play(self, filename):
        try:
            self.stop()
            waveObj = sa.WaveObject.from_wave_file(filename)
            self.logger.info('Now playing' + str(filename) + '.')
            self.playObj = waveObj.play()
        except Exception as e:
            self.logger.info('Error : .' + str(e))
        pass
