from surirobot.core.common import State
import re


class Triggers:

    def __init__(self):
        self.triggers = {}
        self.generateTriggers()

    def generateTriggers(self):
        self.triggers["sound"] = {}
        self.triggers["converse"] = {}
        self.triggers["face"] = {}
        self.triggers["emotion"] = {}
        self.triggers["storage"] = {}
        self.triggers["keyboard"] = {}

        self.triggers["sound"]["new"] = self.newSoundTrigger
        self.triggers["sound"]["available"] = self.availableSoundTrigger

        self.triggers["converse"]["new"] = self.newConverseTrigger

        self.triggers["face"]["unknow"] = self.newPersonTrigger
        self.triggers["face"]["know"] = self.knowPersonTrigger
        self.triggers["face"]["nobody"] = self.nobodyTrigger
        self.triggers["face"]["several"] = self.severalPersonTrigger
        self.triggers["face"]["working"] = self.faceWorking

        self.triggers["emotion"]["new"] = self.newEmotionTrigger
        self.triggers["emotion"]["no"] = self.noEmotionTrigger

        self.triggers["keyboard"]["new"] = self.newKeyboardInput

    # Triggers
    def faceWorking(self, input):
        if not (input["parameters"].get("value") is None):
            if self.services.get("face"):
                if self.services["face"]["datavalue"] == State.FACE_DATAVALUE_WORKING:
                    return input["parameters"]["value"]
                else:
                    return not input["parameters"]["value"]
        return False

    def newPersonTrigger(self, input):
        print(self.__name__)
        # TODO: add sepration new/available with input["parameters"]["new"]
        if self.services.get("face"):
            if self.services["face"]["state"] == State.FACE_UNKNOWN:
                return True
        return False

    def severalPersonTrigger(self, input):
        if self.services.get("face"):
            if self.services["face"]["state"] == State.FACE_MULTIPLES:
                return True
        return False

    def knowPersonTrigger(self, input):
        print(self.__name__)
        # TODO: add sepration new/available with input["parameters"]["new"]
        firstNameRegex = True
        lastNameRegex = True
        fullNameRegex = True
        newCondition = False
        if self.services.get("face"):
            # Check new/available condition
            newParameter = input["parameters"].get("new")
            if newParameter is None or newParameter:
                if self.services["face"]["state"] == State.FACE_KNOWN:
                    newCondition = True
            elif self.services["face"]["state"] == State.FACE_KNOWN or self.services["face"]["state"] == State.FACE_KNOWN_AVAILABLE:
                newCondition = True

            # Check if regex for name is activated
            if input["parameters"].get("name"):
                patternName = re.compile(input["parameters"]["name"])
                if not self.services["face"].get("name"):
                    fullNameRegex = False
                elif patternName.match(self.services["face"]["name"]):
                    fullNameRegex = True
                else:
                    fullNameRegex = False

            # Check if regex for firstname is activated
            if input["parameters"].get("firstname"):
                patternFirstname = re.compile(input["parameters"]["firstname"])
                if not self.services["face"].get("firstname"):
                    firstNameRegex = False
                elif patternFirstname.match(self.services["face"]["firstname"]):
                    firstNameRegex = True
                else:
                    firstNameRegex = False

            # Check if regex for lastname is activated
            if input["parameters"].get("lastname"):
                patternLastname = re.compile(input["parameters"]["lastname"])
                if not self.services["face"].get("lastname"):
                    lastNameRegex = False
                elif patternLastname.match(self.services["face"]["lastname"]):
                    lastNameRegex = True
                else:
                    lastNameRegex = False
        return firstNameRegex and lastNameRegex and newCondition and fullNameRegex

    def nobodyTrigger(self, input):
        if self.services.get("face"):
            # TODO: Implement regex parameters
            if self.services["face"]["state"] == State.FACE_NOBODY:
                return True
        return False

    def newEmotionTrigger(self, input):
        if self.services.get("emotion"):
            if self.services["emotion"]["state"] == State.EMOTION_NEW:
                if input["parameters"].get("emotion"):
                    if self.services["emotion"]["emotion"] == input["parameters"]["emotion"]:
                        return True
                    else:
                        return False
                else:
                    return True
        return False

    def newKeyboardInput(self, input):
        newCondition = False
        if self.services.get("keyboard"):
            # Check new/available condition
            newParameter = input["parameters"].get("new")
            if newParameter is None or newParameter:
                if self.services["keyboard"]["state"] == State.KEYBOARD_NEW:
                    newCondition = True
            elif self.services["keyboard"]["state"] == State.KEYBOARD_AVAILABLE or self.services["keyboard"]["state"] == State.KEYBOARD_AVAILABLE:
                newCondition = True
        return newCondition

    def noEmotionTrigger(self, input):
        if self.services.get("emotion"):
            # TODO: add emotion filter
            if self.services["emotion"]["state"] == State.EMOTION_NO:
                return True
        return False

    def newSoundTrigger(self, input):
        if self.services.get("sound"):
            if self.services["sound"]["state"] == State.SOUND_NEW:
                return True
        return False

    def availableSoundTrigger(self, input):
        if self.services.get("sound"):
            if self.services["sound"]["state"] == State.SOUND_AVAILABLE or self.services["sound"]["state"] == State.SOUND_NEW:
                return True
        return False

    def newConverseTrigger(self, input):
        newCondition = False
        intentCondition = False
        if self.services.get("converse"):
            # Check new/available condition
            newParameter = input["parameters"].get("new")
            if newParameter is None or newParameter:
                if self.services["converse"]["state"] == State.CONVERSE_NEW:
                    newCondition = True
            elif self.services["converse"]["state"] == State.CONVERSE_NEW or self.services["converse"]["state"] == State.CONVERSE_AVAILABLE:
                newCondition = True
            if input["parameters"].get("intent"):
                if self.services["converse"].get("intent"):
                    if self.services["converse"]["intent"] == input["parameters"]["intent"]:
                        intentCondition = True
            else:
                intentCondition = True
        return newCondition and intentCondition


triggers_mg = Triggers()
