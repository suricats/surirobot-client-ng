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


class Actions:
    def __init__(self):
        self.actions = {}

    def generateActions(self):
        try:
            self.actions["playSound"] = self.playSound
            self.actions["converse"] = self.converse
            self.actions["converseAnswer"] = self.converseAnswer
            self.actions["callScenarios"] = self.callScenarios
            self.actions["displayText"] = self.displayText
            self.actions["speak"] = self.speak
            self.actions["wait"] = self.waitFor
            self.actions["takePicture"] = self.addPictureWithUser
            self.actions["listen"] = self.listen
            self.actions["store"] = self.store
            self.actions["changeSuriface"] = self.changeSuriface
            self.actions["activateKeyboardInput"] = self.activateKeyboardInput
            self.actions["updateMemory"] = self.converseUpdateMemory
            self.actions["giveSensorData"] = self.giveSensorData
            return self.actions
        except AttributeError as e:
            raise NotFoundActionException(e.args[0].split("'")[3])
        except Exception:
            raise ActionException()
# Actions

    @staticmethod
    def waitFor(mgr, input):
        if input.get("time"):
            mgr.freeze = True
            QTimer.singleShot(input["time"], mgr.resume_manager)
        else:
            raise MissingParametersActionException("waitFor", 'time')

    @staticmethod
    def store(mgr, input):
        if input.get("list"):
            outputList = mgr.retrieve_data(input["list"])
            mgr.services["storage"].update(outputList)
        else:
            raise MissingParametersActionException("store", 'list')

    @staticmethod
    def addPictureWithUser(mgr, input):
        if input.get("firstname") and input.get("lastname"):
            face_loader.take_picture_new_user(input["firstname"], input["lastname"])
        else:
            raise MissingParametersActionException("addPictureWithUser", ['firstname', 'lastname'])

    @staticmethod
    def playSound(mgr, input):
        if input.get("filepath"):
            serv_ap.play(input["filepath"])
        else:
            raise MissingParametersActionException("playSound", 'filepath')

    @staticmethod
    def displayText(mgr, input):
        text = input.get("text")
        if text:
            if type(text) is str:
                # Manage variables on text
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
                ui.set_text_middle(text)
                mgr.services["storage"]["@text"] = text
            else:
                raise ActionException("displayText", "Type of argument 'text' is not str but {}.".format(type(text).__name__))
        else:
            raise MissingParametersActionException("displayText", 'text')

    @staticmethod
    def speak(mgr, input):
        print('han ouais')
        if input.get("text"):
            mgr.signal_tts_request.emit(input["text"])
        else:
            raise MissingParametersActionException("speak", 'text')

    @staticmethod
    def converse(mgr, input):
        if input.get("filepath"):
            if input.get("id"):
                mgr.signal_nlp_memory.emit("username", serv_fr.idToName(input["id"]), input["id"])
                mgr.signal_converse_audio_with_id.emit(input["filepath"], input["id"])
            else:
                mgr.signal_converse_audio.emit(input["filepath"])
        else:
            raise MissingParametersActionException("converse", 'id')

    @staticmethod
    def converseAnswer(mgr, input):
        if input.get("intent"):
            if input.get("id"):
                mgr.signal_nlp_answer_with_id.emit(input["intent"], input["id"])
            else:
                mgr.signal_nlp_answer.emit(input["intent"])
        else:
            raise MissingParametersActionException("converseAnswer", 'intent')

    @staticmethod
    def converseUpdateMemory(mgr, input):
        if input.get("field") and input.get("value") and input.get("id"):
            mgr.signal_nlp_memory.emit(input["field"], input["value"], input["id"])
        else:
            raise MissingParametersActionException("converseUpdateMemory", ['field', 'value', 'id'])

    @staticmethod
    def listen(mgr, input):
        if input.get("filepath"):
            mgr.signal_stt_request.emit(input["filepath"])
        else:
            raise MissingParametersActionException("listen", 'filepath')

    @staticmethod
    def changeSuriface(mgr, input):
        if input.get("image"):
            mgr.signal_ui_suriface.emit(input["image"])
        else:
            raise MissingParametersActionException("changeSuriface", 'image')

    @staticmethod
    def activateKeyboardInput(mgr, input):
        if not (input.get("activate") is None):
            if input["activate"]:
                ui.activateManualButton.show()
                if input.get("text"):
                    ui.manualLabel.setText(input["text"])
            else:
                ui.activateManualButton.hide()
                ui.manualLayoutContainer.hide()
                ui.manualEdit.setText('')
        else:
            raise MissingParametersActionException("activateKeyboardInput", 'activate')

    @staticmethod
    def callScenarios(mgr, input):
        idTable = input["id"]
        mgr.scope = []
        for id in idTable:
            if type(id) is int:
                mgr.scope.append(id)
            elif type(id) is str:
                mgr.scope += mgr.groups[id]
            else:
                raise ActionException("callScenarios", "Invalid id type {} in new scope.".format(type(id).__name__))
        print('Scope has changed : ' + str(mgr.scope))
        mgr.scopeChanged = True

    @staticmethod
    def giveSensorData(mgr, input):
        if input["type"] and input["output"]:
            token = os.environ.get('API_MEMORY_TOKEN', '')
            url = os.environ.get('API_MEMORY_URL', '')
            headers = {'Authorization': 'Token ' + token}
            r1 = requests.get(url + '/memorize/sensors/last/' + input["type"] + '/', headers=headers)
            last_sensor_data = r1.json()
            print(last_sensor_data)
            if last_sensor_data:
                mgr.services["storage"][input["output"]] = last_sensor_data["data"]

            # Display a nice plot of the last 24 hours
            time_to = int(time.time())
            date_from = datetime.datetime.fromtimestamp(time_to)
            date_from = date_from.replace(hour=0, minute=0, second=0)
            date_to = date_from.replace(day=date_from.day+1)
            time_from = int(date_from.timestamp())
            time_to = int(date_to.timestamp())
            r2 = requests.get(url + '/memorize/sensors/' + str(time_from) + '/' + str(time_to) + '/' + input["type"] + '/', headers=headers)
            # sensors_data = [x for x in r1.json() if x["type"] == input["type"]]
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
                mgr.win.setWindowTitle('{} evolution over since midnight.'.format(input["type"]))

                # Enable antialiasing for prettier plots
                pg.setConfigOptions(antialias=True)
                p1 = mgr.win.addPlot()
                p1.plot(x, y, pen='b')
                p1.setXRange(time_from, time_to)
                # print("x :" + str(x) + "\ny :" + str(y))
                # pg.show()
                mgr.services["storage"][input["output"]] = sensors_data[0]["data"]
        else:
            raise MissingParametersActionException("giveSensorData", ['type', 'output'])


mgr_actions = Actions()
