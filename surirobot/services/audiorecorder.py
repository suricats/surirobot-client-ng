from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import sounddevice as sd
import soundfile as sf
import queue
import uuid
import logging
from surirobot.core import ui

from surirobot.core.common import State, ehpyqtSlot


class AudioRecorder(QThread):
    started_record = pyqtSignal()
    end_record = pyqtSignal(str)

    update_suri_image = pyqtSignal(str)
    update_state = pyqtSignal(str, int, dict)

    def __init__(self, samplerate=44100, channels=1):
        QThread.__init__(self)

        self.samplerate = samplerate
        self.channels = channels

        self.list = queue.Queue()
        self.recording = False

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.update_suri_image.connect(ui.set_image)

    def __del__(self):
        self.wait()
        self.quit()

    def run(self):
        while(True):
            elm = self.list.get()
            self.recording = True
            self.logger.info('Now starting record')

            q = queue.Queue()

            def save_to_file(indata, frames, time, status):
                q.put(indata.copy())

            with sf.SoundFile(elm['filename'], mode='x', samplerate=self.samplerate, channels=self.channels) as file:
                with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=save_to_file):
                    self.started_record.emit()
                    while self.recording:
                        file.write(q.get())

            # self.end_record.emit(elm['filename'])
            self.logger.info('Calling scenario manager...')
            self.update_state.emit("sound", State.SOUND_NEW, {"filepath": elm['filename']})

    @ehpyqtSlot()
    def start_record(self):
        self.list.put({'filename': 'tmp/{}.wav'.format(uuid.uuid4())})
        self.update_suri_image.emit("listening2")

    @ehpyqtSlot()
    def stop_record(self):
        self.recording = False
        self.update_suri_image.emit("basic")

    def is_recording(self):
        return self.recording
