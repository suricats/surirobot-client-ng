from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, QObject
from surirobot.core.api.nlp import NlpApiCaller
from surirobot.core.api.tts import TtsApiCaller
from surirobot.core.api.converse import ConverseApiCaller
from surirobot.core import ui
from surirobot.services import serv_fr


class FaceManager(QObject):
    __instance__ = None

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def __init__(self):
        self.emotional_worker = EmotionalAPICaller(EMOTIONAL_URL)

    def connectToUI(self):
        ###QObject::connect(emotionalWorker,SIGNAL(newReply(QString)),ui,SLOT(setTextDownSignal(QString)));
        #QObject::connect(faceWorker, SIGNAL(newPerson(QString,QString)), ui,SLOT(setTextMiddleSignal(QString)));
        pass

    def startAll(self):
       startEmotionalRecognition();
       startFaceRecognition();
    }

    void faceManager::startFaceRecognition() {
        faceWorker->start();
        faceAPIworker->start();
    }

    def startEmotionalRecognition(self):
        emotionalWorker->start();

    void faceManager::stop()
    {
        emotionalWorker->stop();
        faceWorker->currentThread->quit();
        faceAPIworker->stop();
    }
    bool faceManager::isFaceRecognitionDown() {
        return false;
    }

    bool faceManager::isEmotionalRecognitionDown() {
        return false;
    }
