from PyQt5.QtCore import QThread
import sounddevice as sd
import soundfile as sf
import queue
import uuid
import logging


class AudioRecorder(QThread):
    def __init__(self, samplerate=44100, channels=1):
        QThread.__init__(self)

        self.samplerate = samplerate
        self.channels = channels

        self.q = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.wait()

    def run(self):
        while(True):
            elm = self.q.get()
            self.logger.info('Now recording for {}'.format(elm['duration']))

            record = sd.rec(
                int(elm['duration'] * self.samplerate),
                samplerate=self.samplerate,
                channels=self.channels,
                blocking=True
            )
            sf.write(elm['filename'], record, self.samplerate)

            self.logger.info(
                'Record ended, launching {}'.format(elm['callback'].__name__)
            )
            elm['callback']()

    def record(self, duration, callback):
        elm = {}
        elm['duration'] = duration
        elm['filename'] = 'tmp/{}.wav'.format(uuid.uuid4())
        elm['callback'] = callback
        self.q.put(elm)

        self.logger.info(
            'Adding a {} seconds record to queue'.format(elm['duration'])
        )
