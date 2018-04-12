from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal
from surirobot.services import serv_ap, serv_fr

from surirobot.core.scenario.scenario import Scenario
from surirobot.core.scenario.action import Action
from surirobot.core.scenario.result import Result


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
        self.actions = {}
        self.services = {}

    def generateTriggers(self):
        self.triggers["sound.new"] = self.newSoundTrigger

    def generateActions(self):
        self.actions["playSound"] = self.playSound
        self.actions["converse"] = self.converse

    def loadFile(self, filepath=None):
        newSc = Scenario()
        newSc.triggers = [{"name": "sound.new"}]
        newSc.actions = [{"name": "converse", "filepath": {"source": "trigger", "name": "soud.new", "variable": "filepath"}}]
        self.suscribeToTrigger(newSc)

    def initActions(self, sc):
        for action in sc.actions:
            # Retrieve call function
            action.call = self.actions[action.name]

    def suscribeToTrigger(self, sc):
        for trigger in sc.trigger:
            for key, value in self.triggers:
                if trigger["name"] == key:
                    self.subscriber[key].append(sc)

    @pyqtSlot(str, int, dict)
    def update(self, name, state, data):
        self.services[name] = {}
        self.services[name]['state'] = state
        self.services[name].extend(data)

    def retrieveData(self, action):
        print('motherfucka')

    def checkForTrigger(self, sc):
        output = Result()
        for trigger in sc.triggers:
            func = self.triggers[trigger["name"]]
            if func:
                output.data[trigger["name"]] = func(trigger)
        active = True
        for v in output.data:
            if not v["active"]:
                active = False
                break
        output.active = active
        return output

    def newPersonTrigger(self):
        print('sucka')

    def newSoundTrigger(self):
        print('sounda')

    def playSound(self):
        print('licka')

    def converse(self):
        print('conva')
