from PyQt5.QtCore import QObject, QDir, pyqtSlot, pyqtSignal
from surirobot.services import serv_ap, serv_fr, serv_ar, face_loader, serv_emo
from surirobot.core.api import api_converse, api_nlp, api_tts
from surirobot.core import ui

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
        self.groups = {}
        self.scenarios = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.scopeChanged = False

        # Connect to services
        serv_ar.updateState.connect(self.update)
        api_converse.updateState.connect(self.update)
        api_nlp.updateState.connect(self.update)
        serv_fr.updateState.connect(self.update)
        serv_emo.updateState.connect(self.update)

        self.generateTriggers()
        self.generateActions()

        self.loadFile("/scenario.json")

    def generateTriggers(self):
        self.triggers["sound"] = {}
        self.triggers["converse"] = {}
        self.triggers["face"] = {}
        self.triggers["emotion"] = {}
        self.triggers["storage"] = {}

        self.triggers["sound"]["new"] = self.newSoundTrigger
        self.triggers["sound"]["available"] = self.availableSoundTrigger

        self.triggers["converse"]["new"] = self.newConverseTrigger

        self.triggers["face"]["unknow"] = self.newPersonTrigger
        self.triggers["face"]["know"] = self.knowPersonTrigger
        self.triggers["face"]["nobody"] = self.nobodyTrigger

        self.triggers["emotion"]["new"] = self.newEmotionTrigger
        self.triggers["emotion"]["no"] = self.noEmotionTrigger

    def generateActions(self):
        self.actions["playSound"] = self.playSound
        self.actions["converse"] = self.converse
        self.actions["converseAnswer"] = self.converseAnswer
        self.actions["callScenarios"] = self.callScenarios
        self.actions["displayText"] = self.displayText
        self.actions["speak"] = self.speak
        self.actions["wait"] = self.waitFor
        self.actions["takePicture"] = self.takePicture

    def loadFile(self, filepath=None):
        jsonFile = json.load(open(Dir.BASE + filepath))
        jsonScenarios = jsonFile["scenarios"]
        self.scenarios = {}
        # Load scenarios
        for scenario in jsonScenarios:
            self.scenarios[scenario["id"]] = scenario
        # Load groups of scenarios
        self.groups = jsonFile["groups"]

        # Load initial scope
        for id in jsonFile["initial"]:
            if type(id) is int:
                self.scope.append(id)
            elif type(id) is str:
                print("group : " + str(self.groups[id]))
                self.scope += self.groups[id]
            else:
                print('ERROR : Scenario - loadFile ')
        print('Scope : ' + str(self.scope))

    def loadScenarioFromJson(self, filePath):
        self.scenarios = json.load(open(Dir.SCENARIOS + 'yolo.json'))

    @pyqtSlot(str, int, dict)
    def update(self, name, state, data):
        print('Update of scenarios from ' + name)
        print('\nScope : ' + str(self.scope))
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
                                if valueElement["type"] == "service" and self.services[valueElement["name"]].get(valueElement["variable"], None):
                                    input[name].append({"name": keyElement, "value": self.services[valueElement["name"]][valueElement["variable"]]})
                                else:
                                    input[name].append(valueElement["variable"])
                        else:
                            input[name].append(v)
                elif value["type"] and value["type"] == "service" and self.services[value["name"]].get(value["variable"], None):
                    input[name] = self.services[value["name"]][value["variable"]]
                else:
                    input[name] = value["variable"]
        return input

    def checkForTrigger(self, sc):
        active = True
        for trigger in sc["triggers"]:
            func = self.triggers[trigger["service"]][trigger["name"]]
            if func:
                triggerActive = func(trigger)
            if not triggerActive:
                active = False
                break
        return active

    def checkScope(self):
        for scId in self.scope:
            sc = self.scenarios[scId]
            # print('Scenario : ' + str(scId))
            if self.scopeChanged:
                self.scopeChanged = False
                break
            if self.checkForTrigger(sc):
                self.updateState(sc)
                print('\nScenario ' + str(sc["id"]) + " has been activated\n")
                for action in sc["actions"]:
                    input = self.retrieveData(action)
                    func = self.actions[action["name"]]
                    if func:
                        func(input)
        self.scopeChanged = False

    def updateState(self, sc):
        for trigger in sc["triggers"]:
            # SOUND
            if self.services.get("sound", None):
                if trigger["service"] == "sound" and trigger["name"] == "new" and self.services["sound"]["state"] == State.STATE_SOUND_NEW:
                    self.services["sound"]["state"] = State.STATE_SOUND_AVAILABLE
            # CONVERSE
            if self.services.get("converse", None):
                if trigger["service"] == "converse" and trigger["name"] == "new" and self.services["converse"]["state"] == State.STATE_CONVERSE_NEW:
                    self.services["converse"]["state"] = State.STATE_CONVERSE_AVAILABLE
            # FACE
            if self.services.get("face", None):
                if trigger["service"] == "face" and trigger["name"] == "know" and self.services["face"]["state"] == State.STATE_FACE_KNOWN:
                    self.services["face"]["state"] = State.STATE_FACE_KNOWN_AVAILABLE
                if trigger["service"] == "face" and trigger["name"] == "unknow" and self.services["face"]["state"] == State.STATE_FACE_UNKNOWN:
                    self.services["face"]["state"] = State.STATE_FACE_UNKNOWN_AVAILABLE
                if trigger["service"] == "face" and trigger["name"] == "nobody" and self.services["face"]["state"] == State.STATE_FACE_NOBODY:
                    self.services["face"]["state"] = State.STATE_FACE_NOBODY_AVAILABLE

    # Triggers

    def newPersonTrigger(self, input):
        # TODO: add sepration new/available with input["parameters"]["new"]
        if self.services.get("face", None):
            if self.services["face"]["state"] == State.STATE_FACE_UNKNOWN:
                return True
        return False

    def knowPersonTrigger(self, input):
        # TODO: add sepration new/available with input["parameters"]["new"]
        firstNameRegex = True
        lastNameRegex = True
        fullNameRegex = True
        newCondition = False
        if self.services.get("face", None):
            # Check new/available condition
            newParameter = input["parameters"].get("new", None)
            if newParameter is None or newParameter:
                if self.services["face"]["state"] == State.STATE_FACE_KNOWN:
                    newCondition = True
            elif self.services["face"]["state"] == State.STATE_FACE_KNOWN or self.services["face"]["state"] == State.STATE_FACE_KNOWN_AVAILABLE:
                newCondition = True

            # Check if regex for name is activated
            if input["parameters"].get("name", None):
                patternName = re.compile(input["parameters"]["name"])
                if not self.services["face"].get("name", None):
                    fullNameRegex = False
                elif patternName.match(self.services["face"]["name"]):
                    fullNameRegex = True
                else:
                    fullNameRegex = False

            # Check if regex for firstname is activated
            if input["parameters"].get("firstname", None):
                patternFirstname = re.compile(input["parameters"]["firstname"])
                if not self.services["face"].get("firstname", None):
                    firstNameRegex = False
                elif patternFirstname.match(self.services["face"]["firstname"]):
                    firstNameRegex = True
                else:
                    firstNameRegex = False

            # Check if regex for lastname is activated
            if input["parameters"].get("lastname", None):
                patternLastname = re.compile(input["parameters"]["lastname"])
                if not self.services["face"].get("lastname", None):
                    lastNameRegex = False
                elif patternLastname.match(self.services["face"]["lastname"]):
                    lastNameRegex = True
                else:
                    lastNameRegex = False
        return firstNameRegex and lastNameRegex and newCondition and fullNameRegex

    def nobodyTrigger(self, input):
        if self.services.get("face", None):
            # TODO: Implement regex parameters
            if self.services["face"]["state"] == State.STATE_FACE_NOBODY:
                return True
        return False

    def newEmotionTrigger(self, input):
        if self.services.get("emotion", None):
            if self.services["emotion"]["state"] == State.STATE_EMOTION_NEW:
                if input["parameters"].get("emotion", None):
                    if self.services["emotion"]["emotion"] == input["parameters"]["emotion"]:
                        return True
                    else:
                        return False
                else:
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
            # Check new/available condition
            newParameter = input["parameters"].get("new", None)
            if newParameter is None or newParameter:
                if self.services["converse"]["state"] == State.STATE_CONVERSE_NEW:
                    newCondition = True
            elif self.services["converse"]["state"] == State.STATE_CONVERSE_NEW or self.services["converse"]["state"] == State.STATE_CONVERSE_AVAILABLE:
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
        print('wait')
        # if input.get("time", None):
        #    time.sleep(input["time"])

    def takePicture(self, input):
        face_loader.take_picture()

    def playSound(self, input):
        serv_ap.play(input["filepath"])

    def displayText(self, input):
        print('displayText : ' + str(input))
        text = input.get("text", "")
        list = re.compile("[\{\}]").split(text)
        for index, string in enumerate(list):
            if string.startswith("@"):
                string = string.split("@")[1]
                for element in input["variables"]:
                    if type(element) is dict:
                        if element["name"] == string:
                            list[index] = element["value"]
        text = ""
        text = text.join(list)
        ui.setTextMiddle(text)
        self.services["storage"]["@text"] = text

    def speak(self, input):
        print('\nSPEAK\n')
        api_tts.sendRequest(input["text"])

    def converse(self, input):
        if input.get("id", None):
            api_converse.sendRequest(input["filepath"], input["id"])
        else:
            api_converse.sendRequest(input["filepath"])

    def converseAnswer(self, input):
        if input.get("intent", None):
            if input.get("id", None):
                api_nlp.sendRequest(input["intent"], input["id"])
            else:
                api_nlp.sendRequest(input["intent"])

    def callScenarios(self, input):
        idTable = input["id"]
        self.scope = []
        for id in idTable:
            if type(id) is int:
                self.scope.append(id)
            elif type(id) is str:
                self.scope += self.groups[id]
            else:
                print('ERROR : Scenario - callScenarios ')
        print('Scope has changed : ' + str(self.scope))
        self.scopeChanged = True
