from logging import Logger

from surirobot.services import serv_ap, serv_fr, face_loader
from surirobot.core import ui
from .exceptions import ActionException, NotFoundActionException, MissingParametersActionException

from PyQt5.QtCore import QTimer
import pyqtgraph as pg

import os
import requests
import re
import time
from dateutil import parser
import datetime
import logging

logger = logging.getLogger('Actions')  # type: Logger


class Actions:
    def __init__(self):

        self.actions = {}

    def generate_actions(self):
        try:
            self.actions["playSound"] = self.play_sound
            self.actions["converse"] = self.converse
            self.actions["converseAnswer"] = self.converse_answer
            self.actions["callScenarios"] = self.call_scenarios
            self.actions["displayText"] = self.display_text
            self.actions["speak"] = self.speak
            self.actions["wait"] = self.wait_for
            self.actions["picture"] = self.add_picture_with_user
            self.actions["listen"] = self.listen
            self.actions["store"] = self.store
            self.actions["changeSuriface"] = self.change_suriface
            self.actions["activateKeyboardInput"] = self.activate_keyboard_input
            self.actions["memory"] = self.converse_update_memory
            self.actions["giveSensorData"] = self.give_sensor_data
            self.actions["notifications"] = self.retrieve_notifications
            return self.actions
        except AttributeError as e:
            raise NotFoundActionException(e.args[0].split("'")[3])
        except Exception:
            raise ActionException()

    # Actions

    @staticmethod
    def wait_for(mgr, params):
        if params.get("time"):
            mgr.freeze = True
            QTimer.singleShot(params["time"], mgr.resume_manager)
        else:
            raise MissingParametersActionException("waitFor", 'time')

    @staticmethod
    def store(mgr, params):
        if params.get("list"):
            output_list = mgr.retrieve_data(params["list"])
            mgr.services["storage"].update(output_list)
        else:
            raise MissingParametersActionException("store", 'list')

    @staticmethod
    def add_picture_with_user(mgr, params):
        if params.get("firstname") and params.get("lastname"):
            face_loader.take_picture_new_user(params["firstname"], params["lastname"])
        else:
            raise MissingParametersActionException("addPictureWithUser", ['firstname', 'lastname'])

    @staticmethod
    def play_sound(mgr, params):
        if params.get("filepath"):
            serv_ap.play(params["filepath"])
        else:
            raise MissingParametersActionException("playSound", 'filepath')

    @staticmethod
    def display_text(mgr, params):
        text = params.get("text")
        if text:
            if type(text) is str:
                # Manage variables on text
                text = params.get("text", "")
                str_list = re.compile("[{\}]").split(text)
                for index, string in enumerate(str_list):
                    if string.startswith("@"):
                        string = string.split("@")[1]
                        for element in params["variables"]:
                            if type(element) is dict:
                                if element["name"] == string:
                                    str_list[index] = element["value"]
                text = ""
                text = text.join(str_list)
                ui.set_text_middle(text)
                mgr.services["storage"]["@text"] = text
            else:
                raise ActionException("displayText",
                                      "Type of argument 'text' is not str but {}.".format(type(text).__name__))
        else:
            raise MissingParametersActionException("displayText", 'text')

    @staticmethod
    def speak(mgr, params):
        if params.get("text"):
            mgr.signal_tts_request.emit(params["text"])
        else:
            raise MissingParametersActionException("speak", 'text')

    @staticmethod
    def converse(mgr, params):
        if params.get("filepath"):
            if params.get("id"):
                mgr.signal_nlp_memory.emit("username", serv_fr.idToName(params["id"]), params["id"])
                mgr.signal_converse_audio_with_id.emit(params["filepath"], params["id"])
            else:
                mgr.signal_converse_audio.emit(params["filepath"])
        else:
            raise MissingParametersActionException("converse", 'id')

    @staticmethod
    def converse_answer(mgr, params):
        if params.get("intent"):
            if params.get("id"):
                mgr.signal_nlp_answer_with_id.emit(params["intent"], params["id"])
            else:
                mgr.signal_nlp_answer.emit(params["intent"])
        else:
            raise MissingParametersActionException("converseAnswer", 'intent')

    @staticmethod
    def converse_update_memory(mgr, params):
        if params.get("field") and params.get("value") and params.get("id"):
            mgr.signal_nlp_memory.emit(params["field"], params["value"], params["id"])
        else:
            raise MissingParametersActionException("converseUpdateMemory", ['field', 'value', 'id'])

    @staticmethod
    def listen(mgr, params):
        if params.get("filepath"):
            mgr.signal_stt_request.emit(params["filepath"])
        else:
            raise MissingParametersActionException("listen", 'filepath')

    @staticmethod
    def change_suriface(mgr, params):
        if params.get("image"):
            mgr.signal_ui_suriface.emit(params["image"])
        else:
            raise MissingParametersActionException("changeSuriface", 'image')

    @staticmethod
    def activate_keyboard_input(mgr, params):
        if not (params.get("activate") is None):
            if params["activate"]:
                ui.activateManualButton.show()
                if params.get("text"):
                    ui.manualLabel.setText(params["text"])
            else:
                ui.activateManualButton.hide()
                ui.manualLayoutContainer.hide()
                ui.manualEdit.setText('')
        else:
            raise MissingParametersActionException("activateKeyboardparams", 'activate')

    @staticmethod
    def call_scenarios(mgr, params):
        id_table = params["id"]
        mgr.scope = []
        for scenario_id in id_table:
            if type(scenario_id) is int:
                mgr.scope.append(scenario_id)
            elif type(scenario_id) is str:
                mgr.scope += mgr.groups[scenario_id]
            else:
                raise ActionException("callScenarios",
                                      "Invalid id type {} in new scope.".format(type(scenario_id).__name__))
        logger.debug('Scope has changed : ' + str(mgr.scope))
        mgr.scopeChanged = True

    @staticmethod
    def give_sensor_data(mgr, params):
        if params["type"] and params["output"]:
            token = os.environ.get('API_MEMORY_TOKEN', '')
            url = os.environ.get('API_MEMORY_URL', '')
            headers = {'Authorization': 'Token ' + token}
            r1 = requests.get(url + '/api/memory/sensors/last/' + params["type"] + '/', headers=headers)
            last_sensor_data = r1.json()
            if last_sensor_data:
                mgr.services["storage"][params["output"]] = last_sensor_data["data"]

            # Display a nice plot of the last 24 hours
            time_to = int(time.time())
            date_from = datetime.datetime.fromtimestamp(time_to)
            date_from = date_from.replace(hour=0, minute=0, second=0)
            date_to = date_from.replace(day=date_from.day + 1)
            time_from = int(date_from.timestamp())
            time_to = int(date_to.timestamp())
            r2 = requests.get(
                url + '/api/memory/sensors/' + str(time_from) + '/' + str(time_to) + '/' + params["type"] + '/',
                headers=headers)
            # sensors_data = [x for x in r1.json() if x["type"] == params["type"]]
            sensors_data = r2.json()
            if sensors_data:
                x = []
                y = []
                for data in sensors_data:
                    data["created"] = time.mktime(parser.parse(data["created"]).timetuple())
                    x.append(data["created"])
                    y.append(float(data["data"]))
                sensors_data.sort(key=lambda x: x["created"], reverse=True)
                mgr.win = pg.GraphicsWindow(title="Basic plotting examples")
                mgr.win.resize(1000, 600)
                mgr.win.setWindowTitle('{} evolution over since midnight.'.format(params["type"]))

                # Enable antialiasing for prettier plots
                pg.setConfigOptions(antialias=True)
                p1 = mgr.win.addPlot()
                p1.plot(x, y, pen='b')
                p1.setXRange(time_from, time_to)
                # pg.show()
                mgr.services["storage"][params["output"]] = sensors_data[0]["data"]
        else:
            raise MissingParametersActionException("giveSensorData", ['type', 'output'])

    @staticmethod
    def retrieve_notifications(mgr, params):
        text = ''
        token = os.environ.get('API_MEMORY_TOKEN', '')
        url = os.environ.get('API_MEMORY_URL', '')
        headers = {'Authorization': 'Token ' + token}
        r = requests.get(url + '/api/notifications', headers=headers)
        for notification in r.json():
            if notification.get('type') == 'message' and notification.get('target') == 'all':
                text += notification.get('data', '')

        # Store the notifications
        mgr.services['storage']['@notifications'] = text if text else "Vous n'avez aucune notification"


mgr_actions = Actions()
