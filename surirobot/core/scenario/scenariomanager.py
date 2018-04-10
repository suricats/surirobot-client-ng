from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal
from surirobot.services import serv_ap, serv_fr
from surirobot.core.scenario.scenario import Scenario


class ScenarioManager(QObject):
    __instance__ = None

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):
        QObject.__init__(self)
        self.subscriber = {}
        self.triggers = {}
        self.actions  = {}

    def generateTriggers(self):
        self.triggers["face.newPerson"] = self.newPersonTrigger

    def generateActions(self):
        self.actions["playSound"] = self.playSound

    def loadFile(self, filepath=None):
        newSc = Scenario()
        newSc.triggers = [{"name": "sound.new"}]
        newSc.actions = [{"name": "converse", "filepath": "trigger.sound.new.filepath"}]
        self.suscribeToTrigger(newSc)

    def suscribeToTrigger(self, sc):
        for trigger in sc.trigger:
            for key, value in self.triggers:
                if trigger["name"] == key:
                    self.subscriber[key].append(sc)

    @pyqtSlot(str)
    def update(self,name):
        for sc in self.subscriber[val]:
            r = self.ch=

    def checkForTrigger(self, sc):
        print('fucka ')
    def newPersonTrigger(self):
        print('sucka')

    def playSound(self):
        print('licka')
