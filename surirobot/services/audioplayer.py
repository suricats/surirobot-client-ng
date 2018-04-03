from PyQt5.QtCore import QThread
import sounddevice as sd
import soundfile as sf
import queue
import logging


class AudioPlayer(QThread):
    def __init__(self):
        QThread.__init__(self)

        self.q = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.wait()

    def run(self):
        while(True):
            elm = self.q.get()
            self.logger.info('Now playing {}'.format(elm['filename']))
            sd.play(elm['data'], elm['fs'], blocking=True)

    def play(self, filename):
        elm = {}
        elm['filename'] = filename
        elm['data'], elm['fs'] = sf.read(filename, dtype='float32')
        self.q.put(elm)
        self.logger.info('Adding {} to play queue'.format(filename))
