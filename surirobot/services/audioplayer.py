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
            print(filename)
            self.stop()
            print('A')
            waveObj = sa.WaveObject.from_wave_file(filename)
            print('B')
            self.logger.info('Now playing' + str(filename) + '.')
            print('C')
            self.playObj = waveObj.play()
            print('D')
        except Exception as e:
            self.logger.info('Error : .' + str(e))
        pass
