from PyQt5.QtCore import QThread
from .components.request_tts import TtsApi
from .components.request_download_file import FileDownloader


class TtsService():
    def __init__(self, to_say):
        self.tts = TtsApi(to_say)
        self.thread_tts = QThread()
        self.downloader = FileDownloader()
        self.thread_downloader = QThread()

        self.thread_tts.started.connect(self.tts.sendRequest)
        self.tss.download.connect(self.downloader.)

    def say(self):
        self.thread_tts.start()
        self.thread_downloader.start()
