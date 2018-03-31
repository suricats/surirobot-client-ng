from threading import Thread, Event
import sounddevice as sd
import soundfile as sf
import queue
import logging


class AudioPlayer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stop_event = Event()

        self.q = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self):
        while(not self._stop_event.is_set()):
            elm = self.q.get()
            self.logger.info('Now playing {}'.format(elm['filename']))
            sd.play(elm['data'], elm['fs'], blocking=True)

    def play(self, filename):
        elm = {}
        elm['filename'] = filename
        elm['data'], elm['fs'] = sf.read(filename, dtype='float32')
        self.q.put(elm)
        self.logger.info('Adding {} to play queue'.format(filename))

    def stop(self):
        self._stop_event.set()
