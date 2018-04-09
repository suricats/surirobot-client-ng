from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, QObject
from surirobot.core.api.nlp import NlpApiCaller
from surirobot.core.api.tts import TtsApiCaller
from surirobot.core.api.converse import ConverseApiCaller
from surirobot.core import ui
from surirobot.services import serv_ar


class ConverseManager(QObject):
    NLP_URL = 'https://nlp.api.surirobot.net/getanswer'
    CONVERSE_URL = 'https://converse.api.surirobot.net/converse'
    TTS_URL = 'https://text-to-speech.api.surirobot.net/speak'
    # CONVERSE_URL = 'http://localhost:6900/converse'
    NLP_INTERVAL_REQUEST = 4

    def __init__(self):
        QObject.__init__(self)
        self.debugTimer = QTimer()
        self.debugTimer.setInterval(self.NLP_INTERVAL_REQUEST * 1000)

        self.nlpWorker = NlpApiCaller(self.NLP_URL)
        self.converseWorker = ConverseApiCaller(self.CONVERSE_URL)
        self.speechWorker = TtsApiCaller(self.TTS_URL)

        serv_ar.end_record.connect(self.converseWorker.sendRequest)
        self.converseWorker.new_reply.connect(ui.setTextUp)
        self.nlpWorker.new_reply.connect(ui.setTextUp)

        ### ui.MicButton.released.connect(serv_ar.start_record)
        self.debugTimer.timeout.connect(ui.sendEditText)

        self.nlpDebug = False

    def startConverse(self):
        self.converseWorker.start()

    def startNLP(self):
        self.nlpWorker.start()

    def startTTS(self):
        self.speechWorker.start()

    def startAll(self):
        self.startConverse()
        self.startNLP()
        self.startTTS()

    def stop(self):
        self.nlpWorker.stop()
        self.converseWorker.stop()
        self.debugTimer.stop()
        self.speechWorker.stop()

    def debugNLP(self, set):
        if (self.nlpDebug == set):
            return
        if (set):
            self.nlpDebug = True
            self.debugTimer.start()
        else:
            self.nlpDebug = False
            self.debugTimer.stop()

    def isConverseDown(self):
        return False

    def isNLPDown(self):
        return False
