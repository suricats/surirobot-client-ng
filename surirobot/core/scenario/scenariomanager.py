from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal
from surirobot.services import serv_ap, serv_fr, serv_ar, face_loader
from surirobot.core.api import api_converse, api_nlp, api_tts
from surirobot.core import ui

from surirobot.core.scenario.scenario import Scenario
from surirobot.core.scenario.action import Action
from surirobot.core.common import State, Dir
import logging
import json
import re
import time

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
        self.services = {"face": {}, "emotion": {}, "converse": {}, "sound": {}, "storage": {}}
        self.scope = []
        self.scenarios = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        serv_ar.updateState.connect(self.update)
        api_converse.updateState.connect(self.update)
        serv_fr.updateState.connect(self.update)
        self.generateTriggers()
        self.generateActions()

        self.loadFile()

    def generateTriggers(self):
        self.triggers["sound"] = {}
        self.triggers["converse"] = {}
        self.triggers["face"] = {}
        self.triggers["emotion"] = {}
        self.triggers["storage"] = {}

        self.triggers["sound"]["new"] = self.newSoundTrigger

        self.triggers["converse"]["new"] = self.newConverseTrigger

        self.triggers["face"]["unknow"] = self.newPersonTrigger
        self.triggers["face"]["know"] = self.knowPersonTrigger
        self.triggers["face"]["nobody"] = self.nobodyTrigger

        self.triggers["emotion"]["new"] = self.newEmotionTrigger
        self.triggers["emotion"]["no"] = self.noEmotionTrigger

    def generateActions(self):
        self.actions["playSound"] = self.playSound
        self.actions["converse"] = self.converse
        self.actions["callScenarios"] = self.callScenarios
        self.actions["displayText"] = self.displayText
        self.actions["speak"] = self.speak
        self.actions["wait"] = self.waitFor
        self.actions["takePicture"] = self.takePicture

    def loadFile(self, filepath=None):
        # Wait for audio
        newSc1 = Scenario()
        newSc1.triggers = [{"service": "sound", "name": "new", "parameters": {}}]
        newSc1.actions = [{"name": "converse", "filepath": {"type": "service", "name": "sound", "variable": "filepath"}, "id": {"type": "service", "name": "face", "variable":"id"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [2]}}]
        newSc1.id = 1
        self.scenarios[newSc1.id] = newSc1
        #Wait for converse
        newSc2 = Scenario()
        newSc2.triggers = [{"service": "converse", "name": "new", "parameters": {}}]
        # With this implementation a parameter named "name" is forbidden
        newSc2.actions = [{"name": "playSound", "filepath": {"type": "service", "name": "converse", "variable": "audiopath"}},
        {"name": "displayText", "text": {"type": "service", "name": "converse", "variable": "reply"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [1,3,4]}}]
        newSc2.id = 2
        self.scenarios[newSc2.id] = newSc2
        # Recognize a known person
        newSc3 = Scenario()
        newSc3.triggers = [{"service": "face", "name": "know", "parameters": {}}]
        newSc3.actions = [{"name": "displayText", "text": {"type": "input", "variable": "Oh salut {@firstname} {@lastname} !"}, "variables": [{"firstname": {"type": "service", "name": "face", "variable": "firstname"}}, {"lastname": {"type": "service", "name": "face", "variable": "lastname"}} ]},
        {"name": "callScenarios", "id": {"type": "input", "variable": [1,3,4]}},
        {"name": "speak", "text": {"type": "service", "name": "storage", "variable": "@text"}}]
        newSc3.id = 3
        self.scenarios[newSc3.id] = newSc3

        #Detect a unknown person
        newSc4 = Scenario()
        newSc4.triggers = [{"service": "face", "name": "unknow", "parameters": {}}]
        newSc4.actions = [{"name": "displayText", "text": {"type" : "input", "variable": "Bonjour, je ne t'ai jamais vu ! Veux tu que je t'ajoute ?"}},
        {"name": "speak", "text": {"type": "service", "name": "storage", "variable": "@text"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [5]}}]
        newSc4.id = 4
        self.scenarios[newSc4.id] = newSc4

        # Wait for audio
        newSc5 = Scenario()
        newSc5.triggers = [{"service": "sound", "name": "new", "parameters": {}}]
        newSc5.actions = [{"name": "converse", "filepath": {"type": "service", "name": "sound", "variable": "filepath"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [6,7,8]}}]
        newSc5.id = 5
        self.scenarios[newSc5.id] = newSc5

        # Wait for converse : yes
        newSc6 = Scenario()
        newSc6.triggers = [{"service": "converse", "name": "new", "parameters": {"intent":  "say-yes"}}]
        # With this implementation a parameter named "name" is forbidden
        newSc6.actions = [{"name": "displayText", "text": {"type": "input", "variable": "Préparez-vous !"}},
        {"name": "speak", "text": {"type": "service", "name":"storage", "variable": "@text"}},
        {"name": "wait", "time": {"type": "input", "variable": 4}},
        {"name": "takePicture"},
        {"name": "displayText", "text": {"type": "input", "variable": "Photo enregistrée"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [1,3,4]}}]
        newSc6.id = 6
        self.scenarios[newSc6.id] = newSc6

        # Wait for converse : no
        newSc7 = Scenario()
        newSc7.triggers = [{"service": "converse", "name": "new", "parameters": {"intent":  "say-no"}}]
        # With this implementation a parameter named "name" is forbidden
        newSc7.actions = [{"name": "displayText", "text": {"type": "input", "variable": "Très bien."}},
        {"name": "speak", "text": {"type": "service", "name":"storage", "variable": "@text"}},
        {"name": "wait", "time": {"type": "input", "variable": 2}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [1,3,4]}}]
        newSc7.id = 7
        self.scenarios[newSc7.id] = newSc7

        # Don't understand
        newSc8 = Scenario()
        newSc8.triggers = [{"service": "converse", "name": "new", "parameters": {}}]
        # With this implementation a parameter named "name" is forbidden
        newSc8.actions = [{"name": "displayText", "text": {"type": "input", "variable": "Je n'ai pas compris. Répondez par OUI ou NON."}},
        {"name": "speak", "text": {"type": "service", "name":"storage", "variable": "@text"}},
        {"name": "callScenarios", "id": {"type": "input", "variable": [5]}}]
        newSc8.id = 8
        self.scenarios[newSc8.id] = newSc8
        # First scope
        self.scope.append(newSc1)
        self.scope.append(newSc3)
        self.scope.append(newSc4)

    # WIP
    def loadScenarioFromJson(self, file_path):
        self.scenarios = json.load(open(Dir.SCENARIOS + 'yolo.json'))

    def suscribeToTrigger(self, sc):
        for trigger in sc.trigger:
            for key, value in self.triggers:
                if trigger["name"] == key:
                    self.subscriber[key].append(sc)

    @pyqtSlot(str, int, dict)
    def update(self, name, state, data):
        print('Update of scenarios')
        self.services[name] = {}
        self.services[name]["state"] = state
        self.services[name].update(data)
        self.checkScope()

    def retrieveData(self, action):
        input = {}
        for name, value in action.items():
            if name != "name":
                if type(value) is list:
                    input[name] = []
                    for v in value:
                        if type(v) is dict:
                            for keyElement, valueElement in v.items():
                                if valueElement["type"] == "service":
                                    input[name].append({"name": keyElement, "value" : self.services[valueElement["name"]][valueElement["variable"]]})
                                else:
                                    input[name].append(valueElement["variable"])
                        else:
                            input[name].append(v)
                elif value["type"] and value["type"] == "service":
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
                print('\nScenario ' + str(sc.id) + " has been activated\n")
                for action in sc.actions:
                    input = self.retrieveData(action)
                    func = self.actions[action["name"]]
                    if func:
                        func(input)

    def updateState(self, sc):
        for trigger in sc.triggers:
            if self.services.get("sound", None):
                if trigger["service"] == "sound" and trigger["name"] == "new" and self.services["sound"]["state"] == State.STATE_SOUND_NEW:
                    self.services["sound"]["state"] = State.STATE_SOUND_AVAILABLE
            if self.services.get("converse", None):
                if trigger["service"] == "converse" and trigger["name"] == "new" and self.services["converse"]["state"] == State.STATE_CONVERSE_NEW:
                    self.services["converse"]["state"] = State.STATE_CONVERSE_AVAILABLE

    # Triggers

    def newPersonTrigger(self, input):
        if self.services.get("face", None):
            if self.services["face"]["state"] == State.STATE_FACE_UNKNOWN:
                return True
        return False

    def knowPersonTrigger(self, input):
        if self.services.get("face", None):
            # TODO: Implement regex parameters
            if self.services["face"]["state"] == State.STATE_FACE_KNOWN:
                return True
        return False

    def nobodyTrigger(self, input):
        if self.services.get("face", None):
            # TODO: Implement regex parameters
            if self.services["face"]["state"] == State.STATE_FACE_KNOWN:
                return True
        return False

    def newEmotionTrigger(self, input):
        if self.services.get("emotion", None):
            # TODO: add emotion filter
            if self.services["emotion"]["state"] == State.STATE_EMOTION_NEW:
                return True
        return False

    def noEmotionTrigger(self, input):
        if self.services.get("emotion", None):
            # TODO: add emotion filter
            if self.services["emotion"]["state"] == State.STATE_EMOTION_NO:
                return True
        return False

    def newSoundTrigger(self, input):
        if self.services.get("sound", None):
            if self.services["sound"]["state"] == State.STATE_SOUND_NEW:
                return True
        return False

    def availableSoundTrigger(self, input):
        if self.services.get("sound", None):
            if self.services["sound"]["state"] == State.STATE_SOUND_AVAILABLE or self.services["sound"]["state"] == State.STATE_SOUND_NEW:
                return True
        return False

    def newConverseTrigger(self, input):
        newCondition = False
        intentCondition = False
        if self.services.get("converse", None):
            if input["parameters"].get("new", None):
                if self.services["converse"].get("intent", None):
                    if self.services["converse"]["state"] == State.STATE_CONVERSE_NEW:
                        newCondition = True
            else:
                if self.services["converse"].get("intent", None):
                    if self.services["converse"]["state"] == State.STATE_CONVERSE_NEW or self.services["converse"]["state"] == State.STATE_CONVERSE_AVAILABLE:
                        newCondition = True
            if input["parameters"].get("intent", None):
                if self.services["converse"].get("intent", None):
                    if self.services["converse"]["intent"] == input["parameters"]["intent"]:
                        intentCondition = True
            else:
                intentCondition = True
        return newCondition and intentCondition

    # Actions
    def waitFor(self, input):
        if input.get("time", None):
            time.sleep(input["time"])

    def takePicture(self, input):
        face_loader.take_picture()

    def playSound(self, input):
        serv_ap.play(input["filepath"])

    def displayText(self, input):
        text = input.get("text", "")
        list = re.compile("[\{\}]").split(text)
        for index, string in enumerate(list):
            if string.startswith("@"):
                string = string.split("@")[1]
                for element in input["variables"]:
                    if element["name"] == string:
                        list[index] = element["value"]
        text = ""
        text = text.join(list)
        ui.setTextMiddle(text)
        self.services["storage"]["@text"] = text

    def speak(self, input):
        api_tts.sendRequest(input["text"])

    def converse(self, input):
        if input.get("id", None):
            api_converse.sendRequest(input["filepath"], input["id"])
        else:
            api_converse.sendRequest(input["filepath"])

    def callScenarios(self, input):
        idTable = input["id"]
        self.scope = []
        for id in idTable:
            self.scope.append(self.scenarios[id])
        print('Scope has changed.' + str(self.scope))
