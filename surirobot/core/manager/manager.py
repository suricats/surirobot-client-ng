from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from surirobot.services import serv_ap, serv_fr, serv_ar, face_loader, serv_emo
from surirobot.core.api import api_converse, api_nlp, api_tts, api_stt
from surirobot.core import ui
from surirobot.core.common import State, Dir
from surirobot.core.gui.progressbarupdater import progressBarUpdater
from .triggers import mgr_triggers
from .actions import mgr_actions
import logging
import json
import os
import shutil


class Manager(QObject):
    __instance__ = None
    # Signals
    services_list = ["face", "emotion", "converse", "sound", "storage", "keyboard"]
    signal_tts_request = pyqtSignal(str)
    signal_converse_request_with_id = pyqtSignal(str, int)
    signal_converse_request = pyqtSignal(str)
    signal_converse_update_request = pyqtSignal(str, str, int)
    signal_nlp_request_with_id = pyqtSignal(str, int)
    signal_nlp_request = pyqtSignal(str)
    signal_tts_request = pyqtSignal(str)
    signal_stt_request = pyqtSignal(str)
    signal_ui_suriface = pyqtSignal(str)
    signal_ui_indicator = pyqtSignal(str, str)

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):
        QObject.__init__(self)
        self.triggers = {}
        self.actions = {}
        self.services = {}
        # Generate services
        for service in self.services_list:
            self.services[service] = {}
        self.scope = []
        self.groups = {}
        self.scenarios = {}
        self.win = None
        self.freeze = False
        self.remainingActions = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.scopeChanged = False

        # INPUTS : Connect to services
        serv_ar.updateState.connect(self.update)
        api_converse.updateState.connect(self.update)
        api_nlp.updateState.connect(self.update)
        api_stt.updateState.connect(self.update)
        serv_fr.updateState.connect(self.update)
        ui.updateState.connect(self.update)
        serv_emo.updateState.connect(self.update)

        # OUTPUTS : Connect to services
        self.signal_converse_request.connect(api_converse.sendRequest)
        self.signal_converse_request_with_id.connect(api_converse.sendRequest)
        self.signal_nlp_request_with_id.connect(api_nlp.sendRequest)
        self.signal_nlp_request.connect(api_nlp.sendRequest)
        self.signal_stt_request.connect(api_stt.sendRequest)
        self.signal_tts_request.connect(api_tts.sendRequest)
        self.signal_ui_suriface.connect(ui.setImage)
        self.signal_converse_update_request.connect(api_converse.updateMemory)

        # OUTPUTS : Connect to interface
        self.signal_ui_indicator.connect(ui.changeIndicator)
        serv_fr.signalIndicator.connect(ui.changeIndicator)
        face_loader.signalIndicator.connect(ui.changeIndicator)
        serv_emo.signalIndicator.connect(ui.changeIndicator)
        api_converse.signalIndicator.connect(ui.changeIndicator)
        api_tts.signalIndicator.connect(ui.changeIndicator)

        # Indicators default state
        self.signal_ui_indicator.emit("face", "grey")
        self.signal_ui_indicator.emit("emotion", "grey")
        self.signal_ui_indicator.emit("converse", "grey")

        # Generate actions and triggers
        self.triggers = mgr_triggers.generateTriggers(self.services)
        self.actions = mgr_actions.generateActions()

        self.loadScenarioFile("/scenario.json")

        # Test
        try:
            self.knowUpdater = progressBarUpdater(ui.knowProgressBar, serv_fr.knownTimer, serv_fr.knowElaspedTimer, ui.knowProgressText)
            self.knowUpdater.start()
            self.unknowUpdater = progressBarUpdater(ui.unknowProgressBar, serv_fr.unknownTimer, serv_fr.unknowElaspedTimer, ui.unknowProgressText)
            self.unknowUpdater.start()
            self.nobodyUpdater = progressBarUpdater(ui.nobodyProgressBar, serv_fr.nobodyTimer, serv_fr.nobodyElaspedTimer, ui.nobodyProgressText)
            self.nobodyUpdater.start()
        except Exception as e:
            print("Error - manager" + str(e))

    def loadScenarioFile(self, filepath=None):
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
                print('ERROR : Scenario - loadScenarioFile ')
        print('Scope : ' + str(self.scope))

    @pyqtSlot(str, int, dict)
    def update(self, name, state, data):
        # print('Update of scenarios from ' + name)
        # print('Data : ' + str(data))
        # print('\nScope : ' + str(self.scope))
        # self.services[name] = {}
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
                                if valueElement["type"] == "service" and self.services[valueElement["name"]].get(valueElement["variable"]):
                                    input[name].append({"name": keyElement, "value": self.services[valueElement["name"]][valueElement["variable"]]})
                                else:
                                    input[name].append(valueElement["variable"])
                        else:
                            input[name].append(v)
                elif value.get("type") == "service" and self.services.get(value.get("name")):
                    if self.services[value["name"]].get(value["variable"]):
                        input[name] = self.services[value["name"]][value["variable"]]
                elif type(value) is dict and value.get("variable") is None:
                    input[name] = value
                else:
                    input[name] = value["variable"]
        return input

    def checkForTrigger(self, sc):
        active = True
        for trigger in sc["triggers"]:
            func = self.triggers[trigger["service"]][trigger["name"]]
            if func:
                # print("TRIGGER : " + str(trigger))
                triggerActive = func(self, trigger)
            if not triggerActive:
                active = False
                break
        return active

    def checkScope(self):
        try:
            if not self.freeze:
                for scId in self.scope:
                    sc = self.scenarios[scId]
                    # print('Scenario : ' + str(scId))
                    if self.scopeChanged:
                        self.scopeChanged = False
                        break
                    if self.checkForTrigger(sc):
                        self.updateState(sc)
                        # print('\nScenario ' + str(sc["id"]) + " has been activated\n")
                        for index, action in enumerate(sc["actions"]):
                            input = self.retrieveData(action)
                            func = self.actions[action["name"]]
                            if func:
                                func(self, input)
                                # Special for wait action
                                if self.freeze:
                                    self.remainingActions = sc["actions"][index+1:]
                                    # print('Remaining actions - checkScope : ' + str(self.remainingActions))
                                    break
                self.scopeChanged = False
        except Exception as e:
            print("Error - checkScope")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)

    def updateState(self, sc):
        for trigger in sc["triggers"]:
            # SOUND
            if self.services.get("sound"):
                if trigger["service"] == "sound" and trigger["name"] == "new" and self.services["sound"]["state"] == State.SOUND_NEW:
                    self.services["sound"]["state"] = State.SOUND_AVAILABLE
            # CONVERSE
            if self.services.get("converse"):
                if trigger["service"] == "converse" and trigger["name"] == "new" and self.services["converse"]["state"] == State.CONVERSE_NEW:
                    self.services["converse"]["state"] = State.CONVERSE_AVAILABLE
            # KEYBOARD
            if self.services.get("keyboard"):
                if trigger["service"] == "keyboard" and trigger["name"] == "new" and self.services["keyboard"]["state"] == State.KEYBOARD_NEW:
                    self.services["keyboard"]["state"] = State.KEYBOARD_AVAILABLE
            # FACE
            if self.services.get("face"):
                if trigger["service"] == "face" and trigger["name"] == "know" and self.services["face"]["state"] == State.FACE_KNOWN:
                    self.services["face"]["state"] = State.FACE_KNOWN_AVAILABLE
                if trigger["service"] == "face" and trigger["name"] == "unknow" and self.services["face"]["state"] == State.FACE_UNKNOWN:
                    self.services["face"]["state"] = State.FACE_UNKNOWN_AVAILABLE
                if trigger["service"] == "face" and trigger["name"] == "nobody" and self.services["face"]["state"] == State.FACE_NOBODY:
                    self.services["face"]["state"] = State.FACE_NOBODY_AVAILABLE

    @pyqtSlot()
    def resumeManager(self):
        self.freeze = False
        actions = self.remainingActions[:]
        for index, action in enumerate(actions):
            input = self.retrieveData(action)
            func = self.actions[action["name"]]
            if func:
                func(input)
                # Special for wait action
                if self.freeze:
                    self.remainingActions = actions[index+1:]
                    # print('Remaining actions - resumeManager : ' + str(self.remainingActions))
                    break
        if not self.freeze:
            self.checkScope()

    @pyqtSlot()
    def deleteTemporaryFiles(self):
        for the_file in os.listdir(Dir.TMP):
            if not the_file.startswith("."):
                file_path = os.path.join(Dir.TMP, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
