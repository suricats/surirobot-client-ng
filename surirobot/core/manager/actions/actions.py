import datetime
import logging
import re
import time
import subprocess
from logging import Logger

import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from dateutil import parser

from surirobot.core import ui
from surirobot.core.api import api_memory, api_vocal
from surirobot.services import serv_fr, face_loader, serv_redis
from .exceptions import ActionException, NotFoundActionException, MissingParametersActionException

logger = logging.getLogger('Actions')  # type: Logger


class Actions:
    def __init__(self):

        self.actions = {}

    def generate_actions(self):
        try:
            self.actions["playSound"] = self.play_sound
            self.actions["converse"] = self.converse
            self.actions["vocal"] = self.converse
            self.actions["converseText"] = self.converse_text
            self.actions["callScenarios"] = self.call_scenarios
            self.actions["encodeText"] = self.encode_text
            self.actions["displayText"] = self.display_text
            self.actions["speak"] = self.speak
            self.actions["wait"] = self.wait_for
            self.actions["picture"] = self.add_picture_with_user
            self.actions["picture_without"] = self.add_picture
            self.actions["listen"] = self.listen
            self.actions["store"] = self.store
            self.actions["changeSuriface"] = self.change_suriface
            self.actions["activateKeyboardInput"] = self.activate_keyboard_input
            self.actions["memory"] = self.converse_update_memory
            self.actions["giveSensorData"] = self.give_sensor_data
            self.actions["notifications"] = self.retrieve_notifications
            self.actions["ssh"] = self.ssh_action
            self.actions["redis"] = self.redis_publish
            self.actions["image"] = self.show_image
            self.actions["emotion"] = self.emotion
            return self.actions
        except AttributeError as e:
            raise NotFoundActionException(e.args[0].split("'")[3])
        except Exception:
            raise ActionException()

    # Actions

    @staticmethod
    def wait_for(mgr, params):
        """
        Wait for [time] seconds.

        :param params: dict
        :type mgr: Manager
        """
        if params.get("time"):
            mgr.freeze = True
            QTimer.singleShot(params["time"], mgr.resume_manager)
        else:
            raise MissingParametersActionException("waitFor", 'time')

    @staticmethod
    def store(mgr, params):
        """
        Store a list of variables in the storage service
        The output variable name is the name of the key in [list] dictionnary
        The input variable is taken using the parameter encoder

        :param params: dict
        :type mgr: Manager
        """
        if params.get("list"):
            output_list = mgr.retrieve_data(params["list"])
            mgr.services["storage"].update(output_list)
        else:
            raise MissingParametersActionException("store", 'list')

    @staticmethod
    def add_picture_with_user(mgr, params):
        """
        Take a picture of the camera and create a new user with [firstname] and [lastname]

        :param params: dict
        :type mgr: Manager
        """
        if params.get("firstname") and params.get("lastname"):
            face_loader.take_picture_new_user(params["firstname"], params["lastname"])
        else:
            raise MissingParametersActionException("addPictureWithUser", ['firstname', 'lastname'])

    @staticmethod
    def add_picture(mgr, params):
        """
        Take a picture of the camera and create a new user with [firstname] and [lastname]

        :param params: dict
        :type mgr: Manager
        """
        if params.get("id"):
            face_loader.take_picture_known_user(params["id"])
        else:
            raise MissingParametersActionException("addPicture", ['id'])

    @staticmethod
    def play_sound(mgr, params):
        """

        :param params: dict
        :type mgr: Manager
        """
        if params.get("local") and params.get("message"):
            mgr.signal_audio_play.emit(params["message"], True)
        elif params.get("filepath"):
            mgr.signal_audio_play.emit(params["filepath"], False)
        else:
            raise MissingParametersActionException("playSound", 'filepath')

    @staticmethod
    def encode_text(mgr, params):
        """
        Encode the [text] and store it in storage.@text

        :param params: dict
        :type mgr: Manager
        """
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
                # Store the encoded text in special variable 'text'
                mgr.services["storage"]["@text"] = text
            else:
                raise ActionException("displayText",
                                      "Type of argument 'text' is not str but {}.".format(type(text).__name__))
        else:
            raise MissingParametersActionException("encodeText", 'text')

    @staticmethod
    def display_text(mgr, params):
        """
        Display the [text] and store the result in storage.@displayed_text

        :param params: dict
        :type mgr: Manager
        """
        if params.get("text"):
            # Store the encoded text in special variable 'displayed_text'
            mgr.services["storage"]["@displayed_text"] = params["text"]
            ui.set_text_middle(params["text"])
        else:
            raise MissingParametersActionException("displayText", 'text')

    @staticmethod
    def speak(mgr, params):
        """
        Translate [text] in sound and play it.

        :param params: dict
        :type mgr: Manager
        """
        if params.get("text"):
            mgr.signal_tts_request.emit(params["text"])
        else:
            raise MissingParametersActionException("speak", 'text')

    @staticmethod
    def emotion(mgr, params):
        """
        Call BeyondVerbal API audio endpoint with [filepath] (and [id])

        :param params: dict
        :type mgr: Manager
        """
        if params.get("filepath"):
            #if params.get("id"):
            #    mgr.signal_nlp_memory.emit("username", serv_fr.idToName(params["id"]), params["id"])
            #    mgr.signal_converse_audio_with_id.emit(params["filepath"], params["id"])
            #else:
            mgr.signal_emotional_vocal.emit(params["filepath"], int(params["id"]))
        else:
            raise MissingParametersActionException("emotion", 'id')

    @staticmethod
    def converse(mgr, params):
        """
        Call Converse API audio endpoint with [filepath] (and [id])

        :param params: dict
        :type mgr: Manager
        """
        if params.get("filepath"):
            if params.get("id"):
                mgr.signal_nlp_memory.emit("username", serv_fr.idToName(params["id"]), params["id"])
                mgr.signal_converse_audio_with_id.emit(params["filepath"], params["id"])
            else:
                mgr.signal_converse_audio.emit(params["filepath"])
        else:
            raise MissingParametersActionException("converse", 'id')

    @staticmethod
    def converse_text(mgr, params):
        """
        Call Converse API text endpoint with [filepath] (and [id])

        :param params: dict
        :type mgr: Manager
        """
        if params.get("intent"):
            if params.get("id"):
                mgr.signal_nlp_answer_with_id.emit(params["intent"], params["id"])
            else:
                mgr.signal_nlp_answer.emit(params["intent"])
        else:
            raise MissingParametersActionException("converseText", 'intent')

    @staticmethod
    def converse_update_memory(mgr, params):
        """
        Update the memory of conversation with [field], [value] and [id]

        :param params: dict
        :type mgr: Manager
        """
        if params.get("field") and params.get("value") and params.get("id"):
            mgr.signal_nlp_memory.emit(params["field"], params["value"], params["id"])
        else:
            raise MissingParametersActionException("converseUpdateMemory", ['field', 'value', 'id'])

    @staticmethod
    def listen(mgr, params):
        """
        Translate file in [filepath] in text

        :param params: dict
        :type mgr: Manager
        """
        if params.get("filepath"):
            mgr.signal_stt_request.emit(params["filepath"])
        else:
            raise MissingParametersActionException("listen", 'filepath')

    @staticmethod
    def change_suriface(mgr, params):
        """
        Change the avatar with the [image] id

        :param params: dict
        :type mgr: Manager
        """
        if params.get("image"):
            mgr.signal_ui_suriface.emit(params["image"])
        else:
            raise MissingParametersActionException("changeSuriface", 'image')

    @staticmethod
    def activate_keyboard_input(mgr, params):
        """
        Activate or deactivate keyboard input box depending on [activate] value.

        :param params: dict
        :type mgr: Manager
        """
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
        """
        Change the script tree with all scenario's or group's id in [id] list

        :param params: dict
        :type mgr: Manager
        """
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
        """
        Store [type] sensor information in storage.[output]

        :param params: dict
        :type mgr: Manager
        """
        if params.get("type") and params.get("output"):
            last_sensor_data = api_memory.get_last_sensor(params["type"])
            if last_sensor_data:
                mgr.services["storage"][params["output"]] = last_sensor_data["data"]

            # Display a nice plot of the last 24 hours
            time_to = int(time.time())
            date_from = datetime.datetime.fromtimestamp(time_to).replace(hour=0, minute=0, second=0)
            date_to = date_from.replace(day=date_from.day + 1)
            time_from = int(date_from.timestamp())
            time_to = int(date_to.timestamp())
            # sensors_data = [x for x in r1.json() if x["type"] == params["type"]]
            sensors_data = api_memory.get_sensors(sensor_type=type, t_from=time_from, t_to=time_to)
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
        """
        Store notifications in storage.@notifications

        :param params: dict
        :type mgr: Manager
        """
        text = ''
        notifs = api_memory.get_notifications()
        for notification in notifs:
            if notification.get('type') == 'message' and notification.get('target') == 'all':
                text += notification.get('data', '') + '\n'

        # Store the notifications
        mgr.services['storage']['@notifications'] = text if text else "Vous n'avez aucune notification"

    @staticmethod
    def ssh_action(mgr, params):
        """
        Execute command in ssh

        :param params: dict
        :type mgr: Manager
        """
        if params.get('password') and params.get('host') and params.get('command'):
            command = 'sshpass -p "{}" ssh -o StrictHostKeyChecking=no {} {}'.format(params['password'], params['host'], params['command'])
            subprocess.Popen(command, shell=True)

    @staticmethod
    def redis_publish(mgr, params):
        """
        Listen on specific redis channel

        :param params: dict
        :type mgr: Manager
        """
        if params.get('channel') and params.get('message'):
            serv_redis.redis.publish(params['channel'], params['message'])

    @staticmethod
    def show_image(mgr, params):
        """
        Display the image

        :param params: dict
        :type mgr: Manager
        """
        #TODO passer le tableau de param
        if params.get('image'):
            ui.set_imageViewer("./data/{}.png".format(params['image']))
        else:
            raise MissingParametersActionException("Image_path", 'text')

mgr_actions = Actions()
