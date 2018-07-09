from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from surirobot.services import serv_ap, serv_fr, serv_ar, face_loader, serv_emo
from surirobot.core.api import api_converse, api_nlp, api_tts, api_stt
from surirobot.core import ui
from surirobot.core.common import State, Dir, ehpyqtSlot
from surirobot.core.gui.progressbarupdater import progressBarUpdater
from .triggers.triggers import mgr_triggers
from .actions.actions import mgr_actions
from .exceptions import ManagerException, InitialisationManagerException, BadEncodingScenarioFileException, TypeNotAllowedInDataRetrieverException
import logging
import json
import os
import shutil
import numbers


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
        self.debug = int(os.environ.get('DEBUG', True))
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
        try:
            # INPUTS : Connect to services
            serv_ar.update_state.connect(self.update)
            api_converse.update_state.connect(self.update)
            api_nlp.update_state.connect(self.update)
            api_stt.update_state.connect(self.update)
            serv_fr.update_state.connect(self.update)
            ui.update_state.connect(self.update)
            serv_emo.update_state.connect(self.update)

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
        except Exception as e:
            raise InitialisationManagerException("connecting_signals[{}]".format(type(e).__name__)) from e

        scenario_filepath = os.environ.get("SCENARIO_PATH")
        if scenario_filepath:
            self.load_scenario_file("/scenario.json")
        else:
            raise InitialisationManagerException("scenario_filepath")

        # Connect to progress bars
        try:
            self.knowUpdater = progressBarUpdater(ui.knowProgressBar, serv_fr.knownTimer, serv_fr.knowElaspedTimer, ui.knowProgressText)
            self.knowUpdater.start()
            self.unknowUpdater = progressBarUpdater(ui.unknowProgressBar, serv_fr.unknownTimer, serv_fr.unknowElaspedTimer, ui.unknowProgressText)
            self.unknowUpdater.start()
            self.nobodyUpdater = progressBarUpdater(ui.nobodyProgressBar, serv_fr.nobodyTimer, serv_fr.nobodyElaspedTimer, ui.nobodyProgressText)
            self.nobodyUpdater.start()
        except Exception as e:
            raise InitialisationManagerException("progress_bar_updater[{}]".format(type(e).__name__)) from e

    def load_scenario_file(self, filepath=None):
        try:
            with open(Dir.BASE + filepath) as filepath:
                jsonFile = json.load(filepath)
                jsonScenarios = jsonFile["scenarios"]
                self.scenarios = {}
                self.logger.info('Loaded {} scenarios.'.format(len(jsonScenarios)))
                # Load scenarios
                for scenario in jsonScenarios:
                    self.scenarios[scenario["id"]] = scenario
                # Load groups of scenarios
                self.groups = jsonFile["groups"]
                self.logger.info('Loaded {} groups of scenarios.'.format(len(self.groups)))
                # Load initial scope
                for id in jsonFile["initial"]:
                    if type(id) is int:
                        self.scope.append(id)
                    elif type(id) is str:
                        self.scope += self.groups[id]
                    else:
                        raise InitialisationManagerException('invalid_type_scenario_file')
                if(self.debug):
                    self.logger.info('Scope : {}'.format(self.scope))
        except Exception as e:
            raise BadEncodingScenarioFileException() from e

    @ehpyqtSlot(str, int, dict)
    def update(self, name, state, data):
        if name not in self.services_list:
            raise ManagerException('invalid_service_name', "The service {} doesn't exist.".format(name))
        if(self.debug):
            self.logger.info('Update of scenarios from ' + name)
            # self.logger.info('Data : {}'.format(data))
            # self.logger.info('Scope : {}'.format(self.scope))
        self.services[name]["state"] = state
        self.services[name].update(data)
        self.check_scope()

    def retrieve_data(self, action):
        input = {}
        for name, value in action.items():
            # TODO: Change behaviour to allow variable 'name'
            if name != "name":
                # Case : the parameter is a list
                if type(value) is list:
                    input[name] = []
                    # Browsing the list
                    for v in value:
                        # Case : the element of the list is a dictionnary
                        if type(v) is dict:
                            for keyElement, valueElement in v.items():
                                # Case : the element of the dictionnary is a parameter encoder
                                if self.is_parameter_encoder(valueElement):
                                    # Case : the encoder head to service variable
                                    if valueElement["type"] == "service" and self.services[valueElement["name"]].get(valueElement["variable"]):
                                        input[name].append({"name": keyElement, "value": self.services[valueElement["name"]][valueElement["variable"]]})
                                    # Case : the encoder head to written variable
                                    else:
                                        input[name].append(valueElement["variable"])
                                # Case : the element of the dictonnary is something else (no example 30.06.2018)
                                else:
                                    raise TypeNotAllowedInDataRetrieverException(name, value, v, keyElement, valueElement)
                                    # input[name].append({"name": keyElement, "value": valueElement})
                        # Case : the element of the list is something else
                        else:
                            if isinstance(v, numbers.Number) or isinstance(v, str):
                                input[name].append(v)
                            else:
                                raise TypeNotAllowedInDataRetrieverException(name, value, None, None, v)
                # Case : the parameter is a parameter encoder
                elif self.is_parameter_encoder(value):
                    # Case : the encoder head to service variable
                    if value.get("type") == "service" and self.services.get(value.get("name")):
                        if self.services[value["name"]].get(value["variable"]):
                            input[name] = self.services[value["name"]][value["variable"]]
                    else:
                        input[name] = value["variable"]
                # Case : the parameter is something else
                else:
                    raise TypeNotAllowedInDataRetrieverException(name, None, None, None, value)
                    input[name] = value
            # Case : it's the name of the action
            else:
                pass
        return input

    def check_for_triggers(self, sc):
        active = True
        for trigger in sc["triggers"]:
            func = self.triggers[trigger["service"]][trigger["name"]]
            if func:
                # self.logger.info("Trigger: {}".format(trigger)
                active = func(self, trigger)
            if not active:
                break
        return active

    def check_scope(self):
        try:
            if not self.freeze:
                for scId in self.scope:
                    sc = self.scenarios[scId]
                    # self.logger.info('Scenario : ' + str(scId))
                    if self.scopeChanged:
                        self.scopeChanged = False
                        break
                    if self.check_for_triggers(sc):
                        self.update_state(sc)
                        if self.debug:
                            self.logger.info('Scenario {} has been activated\n'.format(sc["id"]))
                        for index, action in enumerate(sc["actions"]):
                            input = self.retrieve_data(action)
                            func = self.actions[action["name"]]
                            if func:
                                func(self, input)
                                # Store remaining actions while scope is frozen
                                if self.freeze:
                                    if self.debug:
                                        self.logger.info('Scenario engine has been frozen.')
                                    self.remainingActions = sc["actions"][index+1:]
                                    if self.debug:
                                        self.logger.info('Remaining actions: {}'.format(self.remainingActions))
                                    break
                self.scopeChanged = False
        except Exception as e:
            raise ManagerException('check_scope_error', 'An unexpected error occured while checking scope\n{}.'.format(e)) from e

    def update_state(self, sc):
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

    def is_parameter_encoder(self, element):
        if type(element) is dict:
            if element.get("type") is not None and element.get("variable") is not None:
                if element.get("type") == "service" and element.get("name") is not None:
                    return True
                elif element.get("type") == "input":
                    return True
                else:
                    return False
        else:
            return False

    @ehpyqtSlot()
    def resume_manager(self):
        self.freeze = False
        actions = self.remainingActions[:]
        for index, action in enumerate(actions):
            input = self.retrieve_data(action)
            func = self.actions[action["name"]]
            if func:
                func(input)
                # Store remaining actions while scope is frozen
                if self.freeze:
                    self.remainingActions = actions[index+1:]
                    if self.debug:
                        self.logger.info('Remaining actions: {}'.format(self.remainingActions))
                    break
        if not self.freeze:
            self.check_scope()

    @ehpyqtSlot()
    def delete_temporary_files(self):
        for the_file in os.listdir(Dir.TMP):
            if not the_file.startswith("."):
                file_path = os.path.join(Dir.TMP, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.info(e)
