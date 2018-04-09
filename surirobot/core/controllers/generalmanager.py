from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal
from surirobot.core import ui
from surirobot.services import serv_ap, serv_fr
from .conversemanager import ConverseManager
import os
import shutil
from surirobot.core.common import State
from surirobot.core.keypress import KeyPressEventHandler
from surirobot.core.controllers import man_conv


class GeneralManager(QObject):

    TMP_DIR = 'tmp/'

    new_text = pyqtSignal(str)
    say = pyqtSignal(str)
    log_face_reco = pyqtSignal(bool)

    __instance__ = None

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):
        QObject.__init__(self)
        self.eKeyPress = KeyPressEventHandler()
        self.state = State.STATE_IDLE
        self.onScenario = False
        ### self.fm = FaceManager()
        ### QObject::connect(fm->faceWorker, SIGNAL(activateDetectionScenario(State, QByteArray)), this, SLOT(scenarioRecognizedConfirmation(State, QByteArray)));
        self.say.connect(man_conv.speechWorker.sendRequest)
        ### self.log_face_reco.connect(self.fm.faceAPIworker.sendLog)
        self.new_text.connect(ui.setTextMiddle)

    def configureHandlers(self):
        ui.installEventFilter(self.eKeyPress)

    @pyqtSlot()
    def deleteAll(self):
        # Stop the controllers
        ### fm->stop();
        man_conv.stop()
        self.deleteTemporaryFiles()

    def deleteTemporaryFiles(self):
        folder = self.TMP_DIR
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    @pyqtSlot(int, 'QByteArray')
    def scenarioRecognizedConfirmation(self, newState, name):
        if (self.state != newState):
            self.state = newState

            if (newState == self.STATE_IDLE):
                print("STATE IDLE")
                man_conv.converseWorker.intentMode = False
                man_conv.converseWorker.new_intent.connect(self.scenarioRecognizedConfirmation)
            elif (newState == self.STATE_DETECTED):
                print("STATE DETECTED")
                self.nameDetected = name
                man_conv.converseWorker.intentMode = True
                man_conv.converseWorker.new_intent.connect(self.scenarioRecognizedConfirmation)

                text = "Oh ! Salut " + self.nameDetected + " ! Est ce que c'est bien toi ?"
                self.new_text.emit(text)
                self.say.emit(text)

            elif (newState == self.STATE_NOT_DETECTED):
                if (not self.nameDetected.isEmpty()):
                    text = "Au revoir " + self.nameDetected + "."
                    self.new_text.emit(text)
                    self.say.emit(text)

                self.scenarioRecognizedConfirmation(self.STATE_IDLE)

            elif (newState == self.STATE_WAITING_FOR_CONFIRMATION):
                pass

            elif (newState == self.STATE_CONFIRMATION_YES):
                print("STATE YES")
                text = "Parfait ! Chattons ensemble à présent :)"
                self.new_text.emit(text)
                self.say.emit(text)
                self.log_face_reco.emit(True)
                self.scenarioRecognizedConfirmation(self.STATE_IDLE)

            elif (newState == self.STATE_CONFIRMATION_NO):
                print("STATE NO")
                text = "Oh mince je me suis trompé. J'essayerai de faire mieux la prochaine fois !"
                self.new_text.emit(text)
                self.say.emit(text)
                self.log_face_reco.emit(False)
                self.scenarioRecognizedConfirmation(self.STATE_IDLE)

    def activateScenarioRecognizedConfirmation(self, val):
        if (val != self.onScenario):
            self.onScenario = val
            self.eKeyPress.onScenario = val
