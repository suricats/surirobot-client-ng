from PyQt5.QtCore import QTimer
import shared as s


class converseManager():
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
        ### nlpWorker = new NLPAPICaller(NLP_URL);
        ### converseWorker = new ConverseAPICaller(CONVERSE_URL);
        ### speechWorker = new TTSAPICaller(TTS_URL);
        ### QObject::connect(audioRecorder, SIGNAL(newSoundCreated(QString)), converseWorker, SLOT(sendRequest(QString)));
        self.nlpDebug = False
        self.ui = None

    def connectToUI(self, ui):
        self.ui = ui

        ### QObject::connect(converseWorker, SIGNAL(newReply(QString)), ui, SLOT(setTextUpSignal(QString)));
        ### QObject::connect(nlpWorker, SIGNAL(newReply(QString)), ui, SLOT(setTextUpSignal(QString)));
        ### QObject::connect(ui->MicButton, SIGNAL(released()), audioRecorder, SLOT(recordPSeconds()));

        #### QObject::connect(debugTimer, SIGNAL(timeout()), ui, SLOT(sendEditText()));

    def startConverse(self):
        ### converseWorker.start()
        ### audioRecorder.start()
        pass

    def startNLP(self):
        ### nlpWorker.start()
        pass

    def startTTS(self):
        ### speechWorker.start()
        pass

    def startAll(self):
        self.startConverse()
        self.startNLP()
        self.startTTS()

    def stop(self):
        ### nlpWorker.stop()
        ### converseWorker.stop()
        ### debugTimer.stop()
        ### speechWorker.stop()
        ### audioRecorder.currentThread.quit()
        pass

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
