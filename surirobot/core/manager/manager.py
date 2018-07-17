import json
import logging
import numbers
import os
import shutil

from PyQt5.QtCore import QObject, pyqtSignal

from surirobot.core import ui
from surirobot.core.api import api_converse, api_nlp, api_tts, api_stt
from surirobot.core.common import State, Dir, ehpyqtSlot
from surirobot.core.gui.progressbarupdater import progressBarUpdater
from surirobot.services import serv_fr, serv_ar, face_loader, serv_emo
from .actions.actions import mgr_actions
from .exceptions import ManagerException, InitialisationManagerException, BadEncodingScenarioFileException, \
    TypeNotAllowedInDataRetrieverException
from .triggers.triggers import mgr_triggers


def is_parameter_encoder(element):
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


class Manager(QObject):
    __instance__ = None
    # Signals
    services_list = ["face", "emotion", "converse", "sound", "storage", "keyboard"]
    signal_tts_request = pyqtSignal(str)
    signal_converse_audio_with_id = pyqtSignal(str, int)
    signal_converse_audio = pyqtSignal(str)
    signal_nlp_memory = pyqtSignal(str, str, int)
    signal_nlp_answer_with_id = pyqtSignal(str, int)
    signal_nlp_answer = pyqtSignal(str)
    signal_stt_request = pyqtSignal(str)
    signal_ui_suriface = pyqtSignal(str)
    signal_ui_indicator = pyqtSignal(str, str)

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):

        QObject.__init__(self)
        self.debug = os.environ.get('DEBUG', True)
        self.local_voice = os.environ.get('LOCAL_VOICE', False)
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
            self.signal_converse_audio.connect(api_converse.converse_audio)
            self.signal_converse_audio_with_id.connect(api_converse.converse_audio)
            self.signal_nlp_answer_with_id.connect(api_nlp.answer)
            self.signal_nlp_answer.connect(api_nlp.answer)
            self.signal_stt_request.connect(api_stt.recognize)
            self.signal_tts_request.connect(api_tts.speak)
            self.signal_ui_suriface.connect(ui.set_image)
            self.signal_nlp_memory.connect(api_nlp.memory)

            # OUTPUTS : Connect to interface
            self.signal_ui_indicator.connect(ui.change_indicator)
            serv_fr.signal_indicator.connect(ui.change_indicator)
            face_loader.signal_indicator.connect(ui.change_indicator)
            serv_emo.signal_indicator.connect(ui.change_indicator)
            api_converse.signal_indicator.connect(ui.change_indicator)
            api_tts.signal_indicator.connect(ui.change_indicator)

            # Indicators default state
            self.signal_ui_indicator.emit("face", "grey")
            self.signal_ui_indicator.emit("emotion", "grey")
            self.signal_ui_indicator.emit("converse", "grey")

            # Generate actions and triggers
            self.triggers = mgr_triggers.generateTriggers(self.services)
            self.actions = mgr_actions.generate_actions()
        except Exception as e:
            raise InitialisationManagerException("connecting_signals[{}]".format(type(e).__name__)) from e

        scenario_filepath = os.environ.get("SCENARIO_PATH")
        if scenario_filepath:
            self.load_scenario_file("/scenario.json")
        else:
            raise InitialisationManagerException("scenario_filepath")

        # Connect to progress bars
        try:
            self.know_updater = progressBarUpdater(ui.knowProgressBar, serv_fr.knownTimer, serv_fr.knowElaspedTimer, ui.knowProgressText)
            self.know_updater.start()
            self.unknow_updater = progressBarUpdater(ui.unknowProgressBar, serv_fr.unknownTimer, serv_fr.unknowElaspedTimer, ui.unknowProgressText)
            self.unknow_updater.start()
            self.nobody_updater = progressBarUpdater(ui.nobodyProgressBar, serv_fr.nobodyTimer, serv_fr.nobodyElaspedTimer, ui.nobodyProgressText)
            self.nobody_updater.start()
        except Exception as e:
            raise InitialisationManagerException("progress_bar_updater[{}]".format(type(e).__name__)) from e

    def load_scenario_file(self, filepath=None):
        try:
            with open(Dir.BASE + filepath) as filepath:
                json_file = json.load(filepath)
                json_scenarios = json_file["scenarios"]
                self.scenarios = {}
                self.logger.info('Loaded {} scenarios.'.format(len(json_scenarios)))
                # Load scenarios
                for scenario in json_scenarios:
                    self.scenarios[scenario["id"]] = scenario
                # Load groups of scenarios
                self.groups = json_file["groups"]
                self.logger.info('Loaded {} groups of scenarios.'.format(len(self.groups)))
                # Load initial scope
                for scenario_id in json_file["initial"]:  # type: [str,int]
                    if type(scenario_id) is int:
                        self.scope.append(scenario_id)
                    elif type(scenario_id) is str:
                        self.scope += self.groups[scenario_id]
                    else:
                        raise InitialisationManagerException('invalid_type_scenario_file')
                if self.debug:
                    self.logger.info('Scope : {}'.format(self.scope))
        except Exception as e:
            raise BadEncodingScenarioFileException() from e

    @ehpyqtSlot(str, int, dict)
    def update(self, name, state, data):
        if name not in self.services_list:
            raise ManagerException('invalid_service_name', "The service {} doesn't exist.".format(name))
        if self.debug:
            self.logger.info('Update of scenarios from ' + name)
            # self.logger.info('Data : {}'.format(data))
            # self.logger.info('Scope : {}'.format(self.scope))
        self.services[name]["state"] = state
        self.services[name].update(data)
        self.check_scope()

    def retrieve_data(self, action):
        params = {}
        for name, value in action.items():
            # TODO: Change behaviour to allow variable 'name'
            if name != "name":
                # Case : the parameter is a list
                if type(value) is list:
                    params[name] = []
                    # Browsing the list
                    for v in value:
                        # Case : the element of the list is a dictionnary
                        if type(v) is dict:
                            for keyElement, valueElement in v.items():
                                # Case : the element of the dictionnary is a parameter encoder
                                if is_parameter_encoder(valueElement):
                                    # Case : the encoder head to service variable
                                    if valueElement["type"] == "service" and self.services[valueElement["name"]].get(valueElement["variable"]):
                                        params[name].append({"name": keyElement, "value": self.services[valueElement["name"]][valueElement["variable"]]})
                                    # Case : the encoder head to written variable
                                    else:
                                        params[name].append(valueElement["variable"])
                                # Case : the element of the dictonnary is something else (no example 30.06.2018)
                                else:
                                    raise TypeNotAllowedInDataRetrieverException(name, value, v, keyElement, valueElement)
                                    # input[name].append({"name": keyElement, "value": valueElement})
                        # Case : the element of the list is something else
                        else:
                            if isinstance(v, numbers.Number) or isinstance(v, str):
                                params[name].append(v)
                            else:
                                raise TypeNotAllowedInDataRetrieverException(name, value, None, None, v)
                # Case : the parameter is a parameter encoder
                elif is_parameter_encoder(value):
                    # Case : the encoder head to service variable
                    if value.get("type") == "service" and self.services.get(value.get("name")):
                        if self.services[value["name"]].get(value["variable"]):
                            params[name] = self.services[value["name"]][value["variable"]]
                    else:
                        params[name] = value["variable"]
                # Case : the parameter is a dict of parameter encoders
                elif type(value) is dict:
                    for dd_key,dd_value in value.items():
                        if not is_parameter_encoder(dd_value):
                            raise TypeNotAllowedInDataRetrieverException(name, value, None, None, dd_value)
                    params[name] = value
                
                # Case : the parameter is something else
                else:
                    raise TypeNotAllowedInDataRetrieverException(name, None, None, None, value)
                    # input[name] = value
            # Case : it's the name of the action
            else:
                pass
        return params

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
                            params = self.retrieve_data(action)
                            func = self.actions[action["name"]]
                            if func:
                                func(self, params)
                                # Store remaining actions while scope is frozen
                                if self.freeze:
                                    self.remainingActions = sc["actions"][index + 1:]
                                    if self.debug:
                                        self.logger.info('Scenario engine has been frozen.')
                                        self.logger.info('Remaining actions: {}'.format(self.remainingActions))
                                    break
                        # Block the others scenario in the same scope
                        if self.freeze:
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

    @ehpyqtSlot()
    def resume_manager(self):
        self.freeze = False
        actions = self.remainingActions[:]
        for index, action in enumerate(actions):
            params = self.retrieve_data(action)
            func = self.actions[action["name"]]
            if func:
                func(self, params)
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
