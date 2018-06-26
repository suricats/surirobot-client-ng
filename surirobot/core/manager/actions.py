from surirobot.services import serv_ap, serv_fr, serv_ar, face_loader, serv_emo
from PyQt5.QtCore import QTimer
from surirobot.core import ui
import re


class Actions:
    def __init__(self):
        self.actions = {}
        self.generateActions()

    def generateActions(self):
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

# Actions

    def waitFor(self, input):
        if input.get("time"):
            self.freeze = True
            QTimer.singleShot(input["time"], self.resumeManager)
        else:
            self.logger.info('Action(wait) : Missing parameters.')

    def store(self, input):
        if input.get("list"):
            outputList = self.retrieveData(input["list"])
            self.services["storage"].update(outputList)
        else:
            self.logger.info('Action(store) : Missing parameters.')

    def addPictureWithUser(self, input):
        if input.get("firstname") and input.get("lastname"):
            face_loader.take_picture_new_user(input["firstname"], input["lastname"])
        else:
            self.logger.info('Action(takePicture) : Missing parameters.')

    def playSound(self, input):
        if input.get("filepath"):
            serv_ap.play(input["filepath"])
        else:
            self.logger.info('Action(playSound) : Missing parameters.')

    def displayText(self, input):
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
                ui.setTextMiddle(text)
                self.services["storage"]["@text"] = text
            else:
                self.logger.info('Action(displayText) : Invalid type parameter.')
        else:
            self.logger.info('Action(displayText) : Missing parameters.')

    def speak(self, input):
        if input.get("text"):
            self.signal_tts_request.emit(input["text"])
        else:
            self.logger.info('Action(speak) : Missing parameters.')

    def converse(self, input):
        if input.get("filepath"):
            if input.get("id"):
                self.signal_converse_update_request.emit("username", serv_fr.idToName(input["id"]), input["id"])
                self.signal_converse_request_with_id.emit(input["filepath"], input["id"])
            else:
                self.signal_converse_request.emit(input["filepath"])
        else:
            self.logger.info('Action(converse) : Missing parameters.')

    def converseAnswer(self, input):
        if input.get("intent"):
            if input.get("id"):
                self.signal_nlp_request_with_id.emit(input["intent"], input["id"])
            else:
                self.signal_nlp_request.emit(input["intent"])
        else:
            self.logger.info('Action(converseAnswer) : Missing parameters.')

    def converseUpdateMemory(self, input):
        if input.get("field") and input.get("value") and input.get("id"):
            self.signal_converse_update_request.emit(input["field"], input["value"], input["id"])
        else:
            self.logger.info('Action(converseUpdateMemory) : Missing parameters.')

    def listen(self, input):
        if input.get("filepath"):
            self.signal_stt_request.emit(input["filepath"])
        else:
            self.logger.info('Action(listen) : Missing parameters.')

    def changeSuriface(self, input):
        if input.get("image"):
            self.signal_ui_suriface.emit(input["image"])
        else:
            self.logger.info('Action(changeSuriface) : Missing parameters.')

    def activateKeyboardInput(self, input):
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
            self.logger.info('Action(activateKeyboardInput) : Missing parameters.')

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


actions_mg = Actions()
