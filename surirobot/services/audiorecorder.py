from PyQt5.QtCore import QThread, QObject, pyqtSlot, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QAudioRecorder, QAudioEncoderSettings, QMultimedia, QMediaRecorder
import queue
import uuid
import logging
import os


class AudioRecorder(QObject):
    started_record = pyqtSignal()
    end_record = pyqtSignal(str)
    stop_qt_recorder = pyqtSignal()

    def __init__(self, samplerate=44100, channels=1, codec="audio/wave"):
        QObject.__init__(self)

        self.settings = QAudioEncoderSettings()
        self.settings.setCodec(codec)
        self.settings.setSampleRate(samplerate)
        self.settings.setChannelCount(channels)
        self.settings.setQuality(QMultimedia.HighQuality)

        self.recorder = QAudioRecorder()
        self.recorder.setEncodingSettings(self.settings)

        self.stop_qt_recorder.connect(self.recorder.stop)
        self.recorder.stateChanged.connect(self.recorder_state)
        self.current_file = ""

        self.q = queue.Queue()
        self.recording = False

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self):
        while(True):
            url = self.q.get()
            qurl = QUrl(os.getcwd() + '/' + url)

            self.recorder.setOutputLocation(qurl)
            self.recorder.record()

            self.recording = True
            self.logger.info('Now starting record')

    @pyqtSlot()
    def start_record(self):
        url = 'tmp/{}.wav'.format(uuid.uuid4())
        qurl = QUrl(os.getcwd() + '/' + url)
        self.logger.info('FILEPATH: ' + qurl.toString())
        self.current_file = url
        self.recorder.setOutputLocation(qurl)
        self.recorder.record()

        self.recording = True
        self.logger.info('Now starting record')

    @pyqtSlot()
    def stop_record(self):
        self.logger.info("Stopping record")
        self.recording = False
        self.stop_qt_recorder.emit()

    @pyqtSlot('QMediaRecorder::State')
    def recorder_state(self, state):
        if state == QMediaRecorder.StoppedState:
            self.end_record.emit(self.current_file)
            pass

    def is_recording(self):
        return self.recording
