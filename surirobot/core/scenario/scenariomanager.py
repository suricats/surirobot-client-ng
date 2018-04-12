from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal
from surirobot.services import serv_ap, serv_fr, serv_ar
from surirobot.core.api import api_converse, api_nlp, api_tts

from surirobot.core.scenario.scenario import Scenario
from surirobot.core.scenario.action import Action
from surirobot.core.common import State
import logging

class ScenarioManager(QObject):
    __instance__ = None


    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):
        QObject.__init__(self)
        self.triggers = {}
        self.actions = {}
        self.services = {}
        self.scope = []
        self.scenarios = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        serv_ar.updateState.connect(self.update)

    def generateTriggers(self):
        self.triggers["sound"]["new"] = self.newSoundTrigger
        self.triggers["converse"]["new"] = self.newConverseTrigger

    def generateActions(self):
        self.actions["playSound"] = self.playSound
        self.actions["converse"] = self.converse
        self.actions["callScenarios"] = self.callScenarios

    def loadFile(self, filepath=None):
        newSc1 = Scenario()
        newSc1.triggers = [{"service": "sound", "name": "new"}]
        newSc1.actions = [{"name": "converse", "filepath": {"type": "service", "name": "sound", "variable": "filepath"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [2]}}]
        newSc1.id = 1
        self.scenarios[newSc1.id] = newSc1
        self.scope.push(newSc1)
        newSc2 = Scenario()
        newSc2.triggers = [{"service": "converse", "name": "new"}]
        # With this implementation a parameter named "name" is forbidden
        newSc2.actions = [{"name": "playSound", "filepath": {"type": "service", "name": "converse", "variable": "audiopath"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [1]}}]
        newSc2.id = 2
        self.scenarios[newSc2.id] = newSc2

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
        self.logger.info('Scenario update')
        self.services[name] = {}
        self.services[name]["state"] = state
        self.services[name].update(data)
        self.logger.info(self.services)
        self.checkScope()

    def retrieveData(self, action):
        input = {}
        for name, value in action.iteritems():
            if name != "name":
                if value["type"] == "service":
                    input[name] = self.services[value["name"]][value["variable"]]
                else:
                    input[name] = value["variable"]
        return input

    def checkForTrigger(self, sc):
        active = True
        for trigger in sc.triggers:
            func = self.triggers[trigger["service"]][trigger["name"]]
            if func:
                triggerActive = func(trigger)
            if not triggerActive:
                active = False
                break
        return active

    def checkScope(self):
        for sc in self.scope:
            if self.checkForTrigger(sc):
                self.updateState(sc)
                for action in sc.actions:
                    input = self.retrieveData(action)
                    func = self.actions[action["name"]]
                    if func:
                        func(input)

    def updateState(self, sc):
        for trigger in sc.triggers:
            if trigger["service"] == "sound" and trigger["name"] == "new" and self.services["sound"]["state"] == State.STATE_SOUND_NEW:
                self.services["sound"]["state"] == State.STATE_SOUND_AVAILABLE
            if trigger["service"] == "converse" and trigger["name"] == "new" and self.services["converse"]["state"] == State.STATE_CONVERSE_NEW:
                self.services["converse"]["state"] == State.STATE_CONVERSE_AVAILABLE


    # Triggers

    def newPersonTrigger(self):
        print('sucka')

    def newSoundTrigger(self, input):
        if self.services["sound"]["state"] == State.STATE_SOUND_NEW:
            return True
        return False

    def newConverseTrigger(self, input):
        newCondition = False
        intentCondition = False
        if input["new"]:
            if self.services["converse"]["state"] == State.STATE_CONVERSE_NEW:
                newCondition = True
        else:
            if self.services["converse"]["state"] == State.STATE_CONVERSE_NEW or self.services["converse"]["state"] == State.STATE_CONVERSE_AVAILABLE:
                newCondition = True
        if input["intent"]:
            if self.services["converse"]["intent"] == input["intent"]:
                intentCondition = True
        else:
            intentCondition = True
        return newCondition and intentCondition

    # Actions

    def playSound(self, input):
        serv_ap.play(input["filepath"])

    def converse(self, input):
        api_converse.sendRequest(input["filepath"])

    def callScenarios(self, input):
        idTable = input["id"]["variable"]
        self.scope = []
        for id in idTable:
            self.scope.push(self.scenarios[id])
