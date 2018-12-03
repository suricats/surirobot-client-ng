import json
import logging
import numbers
import os
import shutil

from PyQt5.QtCore import QObject, pyqtSignal

from surirobot.core import ui
from surirobot.core.api import api_converse, api_nlp, api_tts, api_stt, api_vocal
from surirobot.core.common import State, Dir, ehpyqtSlot
from surirobot.core.gui.progressbarupdater import progressBarUpdater
from surirobot.services import serv_fr, face_loader, serv_emo
from surirobot.devices import serv_ar, serv_ap
from .actions.actions import mgr_actions
from .exceptions import ManagerException, InitialisationManagerException, BadEncodingScenarioFileException, \
    TypeNotAllowedInDataRetrieverException
from .triggers.triggers import mgr_triggers


def is_parameter_encoder(element):
    """
    Check if element is a parameter encoder

    Example:
    "text":{"type": "service", "name": "storage", "variable": "@text"}

    Parameters
    ----------
    element : object

    Returns
    -------
    bool
    """
    if type(element) is dict:
        if element.get("type") is not None and element.get("variable") is not None:
            if element.get("type") == "service" and element.get("name") is not None:
                return True
            elif element.get("type") == "input":
                return True
    return False


class Manager(QObject):
    """
    Manage all services, devices and api callers around scenarios and scopes
    """
    __instance__ = None
    # Signals
    services_list = ["face", "emotion", "converse", "sound", "storage", "keyboard", "redis"]
    signal_tts_request = pyqtSignal(str)
    signal_converse_audio_with_id = pyqtSignal(str, int)
    signal_converse_audio = pyqtSignal(str)
    signal_emotional_vocal_with_id = pyqtSignal(str, str, int)
    signal_emotional_vocal = pyqtSignal(str)
    signal_nlp_memory = pyqtSignal(str, str, int)
    signal_nlp_answer_with_id = pyqtSignal(str, int)
    signal_nlp_answer = pyqtSignal(str)
    signal_stt_request = pyqtSignal(str)
    signal_ui_suriface = pyqtSignal(str)
    signal_ui_indicator = pyqtSignal(str, str)
    signal_audio_play = pyqtSignal(str, bool)

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = QObject.__new__(cls)
        return cls.__instance__

    def __init__(self):

        QObject.__init__(self)
        self.local_voice = bool(int(os.environ.get('LOCAL_VOICE', False)))
        self.triggers = {}
        self.actions = {}
        self.services = {}
        self.images_list = []
        # Generate services
        for service in self.services_list:
            self.services[service] = {}
        self.scope = []
        self.groups = {}
        self.scenarios = {}
        self.templates = {}
        self.win = None
        self.freeze = False
        self.remainingActions = []
        self.logger = logging.getLogger(type(self).__name__)
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
            self.signal_converse_audio.connect(api_vocal.getAnalysis)
            self.signal_emotional_vocal.connect(api_vocal.getAnalysis)
            self.signal_emotional_vocal_with_id.connect(api_vocal.getAnalysis)
            self.signal_nlp_answer_with_id.connect(api_nlp.answer)
            self.signal_nlp_answer.connect(api_nlp.answer)
            self.signal_stt_request.connect(api_stt.recognize)
            self.signal_tts_request.connect(api_tts.speak)
            self.signal_ui_suriface.connect(ui.set_image)
            self.signal_nlp_memory.connect(api_nlp.memory)
            self.signal_audio_play.connect(serv_ap.play)

            # OUTPUTS : Connect to interface

            self.signal_ui_indicator.connect(ui.change_indicator)
            serv_fr.signal_indicator.connect(ui.change_indicator)
            face_loader.signal_indicator.connect(ui.change_indicator)
            serv_emo.signal_indicator.connect(ui.change_indicator)
            api_converse.signal_indicator.connect(ui.change_indicator)
            api_tts.signal_indicator.connect(ui.change_indicator)
            api_nlp.signal_indicator.connect(ui.change_indicator)

            # Indicators default state
            self.signal_ui_indicator.emit("face", "grey")
            self.signal_ui_indicator.emit("emotion", "grey")
            self.signal_ui_indicator.emit("converse", "grey")

            # Generate actions and triggers
            self.triggers = mgr_triggers.generate_triggers(self.services)
            self.actions = mgr_actions.generate_actions()
        except Exception as e:
            raise InitialisationManagerException("connecting_signals[{}]".format(type(e).__name__)) from e

        scenario_file_path = os.environ.get("SCENARIO_PATH")
        if scenario_file_path:
            self.load_scenario_file(scenario_file_path)
        else:
            raise InitialisationManagerException("scenario_file_path")

        image_path = os.environ.get("IMAGE_PATH")
        if image_path:
            self.load_list_image(image_path)
        else:
            raise InitialisationManagerException("image_path")

        # Connect to progress bars
        try:
            self.know_updater = progressBarUpdater(bar=ui.knowProgressBar, timer=serv_fr.knownTimer, text=ui.knowProgressText)
            self.know_updater.start()
            self.unknow_updater = progressBarUpdater(bar=ui.unknowProgressBar, timer=serv_fr.unknownTimer, text=ui.unknowProgressText)
            self.unknow_updater.start()
            self.nobody_updater = progressBarUpdater(bar=ui.nobodyProgressBar, timer=serv_fr.nobodyTimer, text=ui.nobodyProgressText)
            self.nobody_updater.start()
        except Exception as e:
            raise InitialisationManagerException("progress_bar_updater[{}]".format(type(e).__name__)) from e

    def load_scenario_file(self, file_path=None):
        """
        Load scenarios, groups, templates and initial scope from json file

        Parameters
        ----------
        file_path : str
            The path of the json file.
        """
        try:
            with open(Dir.BASE + '/' + file_path) as file_path:
                json_file = json.load(file_path)
                json_scenarios = json_file["scenarios"]
                self.scenarios = {}
                self.logger.info('Loaded {} scenarios.'.format(len(json_scenarios)))
                # Load scenarios
                for scenario in json_scenarios:
                    self.scenarios[scenario["id"]] = scenario
                # Load groups of scenarios
                self.groups = json_file["groups"]
                self.logger.info('Loaded {} groups of scenarios.'.format(len(self.groups)))
                self.templates = json_file["templates"]
                self.logger.info('Loaded {} templates.'.format(len(self.templates)))
                # Load initial scope
                for scenario_id in json_file["initial"]:  # type: [str,int]
                    if type(scenario_id) is int:
                        self.scope.append(scenario_id)
                    elif type(scenario_id) is str:
                        self.scope += self.groups[scenario_id]
                    else:
                        raise InitialisationManagerException('invalid_type_scenario_file')
                self.logger.debug('Scope : {}'.format(self.scope))
        except Exception as e:
            raise BadEncodingScenarioFileException() from e

    def load_list_image(self, image_path):
        """
        Load image list to show

        Parameters
        ----------
         image_path : str
            The path of the image.
        """
        for file in os.listdir(image_path):
            if file.endswith(".jpg") or file.endswith(".png"):
                self.logger.debug('Image List add : {}'.format((os.path.join(image_path, file))))
                self.images_list.append(file)

    @ehpyqtSlot(str, int, dict)
    def update(self, name, state, data):
        """
        Slot called by service when it updates.
        Change the state and the data of the service.

        Parameters
        ----------
        data
            dict
        state
            int
        name
            str
        """
        if name not in self.services_list:
            raise ManagerException('invalid_service_name', "The service {} doesn't exist.".format(name))
        if int(os.environ.get('DEBUG', '0')) >= 2 or (int(os.environ.get('DEBUG', '0')) == 1 and name != 'face' and 'working' not in data):
            self.logger.debug('Update of scenarios from ' + name)
            self.logger.debug('Data : {}'.format(data))
            self.logger.debug('Scope : {}'.format(self.scope))
        if state != State.NO_STATE:
            self.services[name]["state"] = state
        self.services[name].update(data)
        self.check_scope()

    def retrieve_data(self, action):
        """
        Convert data encodings into real values
        Can convert if parameter is :

        - list
            - dict
            - parameter encoder
        - parameter encoder
        - dict
            - parameter encoder
        Parameters
        ----------
        action
            dict
        """
        params = {}
        for name, value in action.items():
            # TODO: Change behaviour to allow variable 'name'
            if name != "name":
                # Case : the parameter is a list
                if type(value) is list:
                    params[name] = []
                    # Browsing the list
                    for v in value:
                        # Case : the element of the list is a dictionary
                        if type(v) is dict:
                            for keyElement, valueElement in v.items():
                                # Case : the element of the dictionary is a parameter encoder
                                if is_parameter_encoder(valueElement):
                                    # Case : the encoder head to service variable
                                    if valueElement["type"] == "service" and self.services[valueElement["name"]].get(valueElement["variable"]):
                                        params[name].append({"name": keyElement, "value": self.services[valueElement["name"]][valueElement["variable"]]})
                                    # Case : the encoder head to written variable
                                    else:
                                        params[name].append(valueElement["variable"])
                                # Case : the element of the dictionary is something else (no example 30.06.2018)
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
                    for dd_key, dd_value in value.items():
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
        """
        Check if triggers of scenario are active

        Returns
        -------
        bool
        Parameters
        ----------
        sc
            dict

        """
        active = True
        for trigger in sc["triggers"]:
            func = self.triggers[trigger["service"]][trigger["name"]]
            if func:
                # self.logger.debug("Trigger of {}: {}".format(sc['id'], trigger))
                active = func(self, trigger)
            if not active:
                break
        return active

    def check_scope(self):
        """
       Check if on the actual scope, one scenario need to be activated
       If so, the scenario is activated and executes its actions
       """
        try:
             if not self.freeze:
                for scId in self.scope:
                    sc = self.scenarios[scId]
                    if self.scopeChanged:
                        self.scopeChanged = False
                        break
                    if self.check_for_triggers(sc):
                        self.update_state(sc)
                        self.logger.debug('Scenario {} has been activated\n'.format(sc["id"]))
                        # Retrieve layouts
                        actions = sc["actions"]
                        before_actions = []
                        after_actions = []
                        if sc.get('templates'):
                            self.logger.debug('Templates detected  : {}'.format(sc['templates']))
                            for template_name in sc['templates']:
                                if self.templates.get(template_name):
                                    if self.templates[template_name].get('before'):
                                        before_actions += self.templates[template_name]['before']
                                    if self.templates[template_name].get('after'):
                                        after_actions += self.templates[template_name]['after']
                                else:
                                    raise ManagerException('check_scope_error', 'Invalid template name {} in scenario n°{}'.format(template_name, sc['id']))
                        actions = before_actions + actions + after_actions
                        self.logger.debug('List of actions : {}'.format(actions))
                        for index, action in enumerate(actions):
                            params = self.retrieve_data(action)
                            func = self.actions[action["name"]]
                            self.logger.debug('Action called : {}:{}'.format(func.__name__, params))
                            if func:
                                func(self, params)
                                # Store remaining actions while scope is frozen
                                if self.freeze:
                                    self.remainingActions = actions[index + 1:]
                                    self.logger.info('Scenario engine has been frozen.')
                                    self.logger.debug('Remaining actions: {}'.format(self.remainingActions))
                                    break
                        # Block the others scenario in the same scope
                        if self.freeze:
                            break
                self.scopeChanged = False
        except Exception as e:
            raise ManagerException('check_scope_error', 'An unexpected error occurred while checking scope\n{}.'.format(e)) from e

    def update_state(self, sc):
        """
        Update the state of scenarios if needed after an activation of a scenario

        Parameters
        ----------
        sc
            dict
       """
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
        """
        Slot called after wait action that unfreeze the manager and executes the remaining actions

        """
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
                    self.logger.debug('[R] Remaining actions: {}'.format(self.remainingActions))
                    break
        if not self.freeze:
            self.check_scope()

    @ehpyqtSlot()
    def delete_temporary_files(self):
        """
        Delete temporary files
        """
        for the_file in os.listdir(Dir.TMP):
            if not the_file.startswith("."):
                file_path = os.path.join(Dir.TMP, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.error('{} occurred while deleting temporary files.\n{}'.format(type(e).__name__, e))
    
    def change_current_scenario(self, group_id):
        self.scope = self.groups[group_id]
        self.check_scope()
