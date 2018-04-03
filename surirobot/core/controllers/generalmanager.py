from PyQt5.QtCore import QObject, QDir
from surirobot.core import ui, serv_ap
import os, shutil


class GeneralManager(QObject):

    TMP_DIR = 'tmp/'
    STATE_IDLE = 0
    STATE_DETECTED = 1
    STATE_NOT_DETECTED = 2
    STATE_WAITING_FOR_CONFIRMATION = 3
    STATE_CONFIRMATION_YES = 4
    STATE_CONFIRMATION_NO = 5

    def __init__(self):
        ### eKeyPress = new keyPressEventHandler();
        self.state = self.STATE_IDLE
        self.onScenario = False
        ### cm = converseManager::getInstance();
        ### fm = faceManager::getInstance();
        ### QObject::connect(this, SIGNAL(newText(QString)), ui, SLOT(setTextMiddleSignal(QString)));
        ### QObject::connect(fm->faceWorker, SIGNAL(activateDetectionScenario(State, QByteArray)), this, SLOT(scenarioRecognizedConfirmation(State, QByteArray)));
        ### QObject::connect(this, SIGNAL(say(QString)), cm->speechWorker, SLOT(sendRequest(QString)));
        ### QObject::connect(this, SIGNAL(faceRecognitionLog(bool)), fm->faceAPIworker, SLOT(sendLog(bool)));

    def configureHandlers(self, ui):
        ### ui->installEventFilter(eKeyPress)
        pass

    def deleteAll():
        # Stop the controllers
        ### fm->stop();
        ### cm->stop();
        self.deleteTemporaryFiles()

    def deleteTemporaryFiles(self):
        folder = self.TMP_DIR
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def scenarioRecognizedConfirmation(self, newState, name):
        if (self.state != newState):
            self.state = newState

            if (newState == self.STATE_IDLE):
                print("STATE IDLE")
                ### cm->converseWorker->intentMode = false;
                ### QObject::disconnect(cm->converseWorker, SIGNAL(newIntent(State, QByteArray)), this, SLOT(scenarioRecognizedConfirmation(State, QByteArray)));
            elif (newState == self.STATE_DETECTED):
                print("STATE DETECTED")
                self.nameDetected = name
                ### cm->converseWorker->intentMode = True

                ### QObject::connect(cm->converseWorker, SIGNAL(newIntent(State, QByteArray)), this, SLOT(scenarioRecognizedConfirmation(State, QByteArray)));

                text = "Oh ! Salut " + self.nameDetected + " ! Est ce que c'est bien toi ?"
                ### emit newText(text)
                ### emit say(text)

            elif (newState == self.STATE_NOT_DETECTED):
                if (not self.nameDetected.isEmpty()):
                    text = "Au revoir " + self.nameDetected + "."
                    ### emit newText(text)
                    ### emit say(text)

                self.scenarioRecognizedConfirmation(self.STATE_IDLE)

            elif (newState == self.STATE_WAITING_FOR_CONFIRMATION):
                pass

            elif (newState == self.STATE_CONFIRMATION_YES):
                print("STATE YES")
                text = "Parfait ! Chattons ensemble à présent :)"
                ### emit newText(text)
                ### emit say(text)
                ### emit faceRecognitionLog(true)
                self.scenarioRecognizedConfirmation(self.STATE_IDLE)

            elif (newState == self.STATE_CONFIRMATION_NO):
                print("STATE NO")
                text = "Oh mince je me suis trompé. J'essayerai de faire mieux la prochaine fois !"
                ### emit newText(text)
                ### emit say(text)
                ### emit faceRecognitionLog(False)
                scenarioRecognizedConfirmation(self.STATE_IDLE)

    def activateScenarioRecognizedConfirmation(self, val):
        if (val != self.onScenario):
            self.onScenario = val
            ### eKeyPress.onScenario = val
