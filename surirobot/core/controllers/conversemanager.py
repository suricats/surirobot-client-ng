from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, QObject
from surirobot.core.api.nlp import NlpApiCaller
from surirobot.core.api.tts import TtsApiCaller
from surirobot.core.api.converse import ConverseApiCaller
from surirobot.core import ui


class converseManager(QObject):
    NLP_URL = 'https://nlp.api.surirobot.net/getanswer'
    CONVERSE_URL = 'https://converse.api.surirobot.net/converse'
    TTS_URL = 'https://text-to-speech.api.surirobot.net/speak'
    # CONVERSE_URL = 'http://localhost:6900/converse'
    NLP_INTERVAL_REQUEST = 4

    __instance__ = None

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        return cls.instance

    def __init__(self):
        self.debugTimer = QTimer()
        self.debugTimer.setInterval(self.NLP_INTERVAL_REQUEST * 1000)

        ### audioRecorder = new SpeechRecording;
        self.nlpWorker = NlpApiCaller(self.NLP_URL)
        self.converseWorker = ConverseApiCaller(self.CONVERSE_URL)
        self.speechWorker = TtsApiCaller(self.TTS_URL)
        ### QObject::connect(audioRecorder, SIGNAL(newSoundCreated(QString)), converseWorker, SLOT(sendRequest(QString)));

        self.nlpDebug = False

    def connectToUI(self):
        self.converseWorker.new_reply.connect(ui.setTextUp)
        self.nlpWorker.new_reply.connect(ui.setTextUp)

        ### QObject::connect(ui->MicButton, SIGNAL(released()), audioRecorder, SLOT(recordPSeconds()));
        ### QObject::connect(debugTimer, SIGNAL(timeout()), ui, SLOT(sendEditText()));

    def startConverse(self):
        self.converseWorker.start()
        ### self.audioRecorder.start()

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
        ### audioRecorder.currentThread.quit()

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
