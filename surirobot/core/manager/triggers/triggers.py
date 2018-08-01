from surirobot.core.common import State
import re
import logging

logger = logging.getLogger('Triggers')


class Triggers:

    def __init__(self):
        self.triggers = {}

    def generateTriggers(self, services):
        # Generate services domain for triggers
        for service in services:
            self.triggers[service] = {}

        # Register triggers
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
        return self.triggers

    # Triggers
    @staticmethod
    def faceWorking(mgr, input):
        if not (input["parameters"].get("value") is None):
            if mgr.services.get("face"):
                if mgr.services["face"]["working"]:
                    return input["parameters"]["value"]
                else:
                    return not input["parameters"]["value"]
        return False

    @staticmethod
    def newPersonTrigger(mgr, input):
        # TODO: add separation new/available with input["parameters"]["new"]
        if mgr.services.get("face"):
            if mgr.services["face"].get("state") is not None:
                if mgr.services["face"]["state"] == State.FACE_UNKNOWN:
                    return True
        return False

    @staticmethod
    def severalPersonTrigger(mgr, input):
        if mgr.services.get("face"):
            if mgr.services["face"].get("state") is not None:
                if mgr.services["face"]["state"] == State.FACE_MULTIPLES:
                    return True
        return False

    @staticmethod
    def knowPersonTrigger(mgr, input):
        # TODO: add sepration new/available with input["parameters"]["new"]
        first_name_regex = True
        last_name_regex = True
        full_name_regex = True
        new_condition = False
        if mgr.services.get("face"):
            if mgr.services["face"].get("state") is not None:
                # Check new/available condition
                newParameter = input["parameters"].get("new")
                if newParameter is None or newParameter:
                    if mgr.services["face"]["state"] == State.FACE_KNOWN:
                        new_condition = True
                elif mgr.services["face"]["state"] == State.FACE_KNOWN or mgr.services["face"]["state"] == State.FACE_KNOWN_AVAILABLE:
                    new_condition = True
                # Check if regex for name is activated
                if input["parameters"].get("name"):
                    patternName = re.compile(input["parameters"]["name"])
                    if not mgr.services["face"].get("name"):
                        full_name_regex = False
                    elif patternName.match(mgr.services["face"]["name"]):
                        full_name_regex = True
                    else:
                        full_name_regex = False

                # Check if regex for firstname is activated
                if input["parameters"].get("firstname"):
                    patternFirstname = re.compile(input["parameters"]["firstname"])
                    if not mgr.services["face"].get("firstname"):
                        first_name_regex = False
                    elif patternFirstname.match(mgr.services["face"]["firstname"]):
                        first_name_regex = True
                    else:
                        first_name_regex = False

                # Check if regex for lastname is activated
                if input["parameters"].get("lastname"):
                    patternLastname = re.compile(input["parameters"]["lastname"])
                    if not mgr.services["face"].get("lastname"):
                        last_name_regex = False
                    elif patternLastname.match(mgr.services["face"]["lastname"]):
                        last_name_regex = True
                    else:
                        last_name_regex = False
        # logger.debug('know_person_trigger : {},{},{},{}'.format(first_name_regex, last_name_regex, new_condition, full_name_regex))
        return first_name_regex and last_name_regex and new_condition and full_name_regex

    @staticmethod
    def nobodyTrigger(mgr, input):
        if mgr.services.get("face"):
            # TODO: Implement regex parameters
            if mgr.services["face"].get("state") == State.FACE_NOBODY:
                return True
        return False

    @staticmethod
    def newEmotionTrigger(mgr, input):
        if mgr.services.get("emotion"):
            if mgr.services["emotion"]["state"] == State.EMOTION_NEW:
                if input["parameters"].get("emotion"):
                    if mgr.services["emotion"]["emotion"] == input["parameters"]["emotion"]:
                        return True
                    else:
                        return False
                else:
                    return True
        return False

    @staticmethod
    def newKeyboardInput(mgr, input):
        newCondition = False
        if mgr.services.get("keyboard"):
            # Check new/available condition
            newParameter = input["parameters"].get("new")
            if newParameter is None or newParameter:
                if mgr.services["keyboard"]["state"] == State.KEYBOARD_NEW:
                    newCondition = True
            elif mgr.services["keyboard"]["state"] == State.KEYBOARD_AVAILABLE or mgr.services["keyboard"]["state"] == State.KEYBOARD_AVAILABLE:
                newCondition = True
        return newCondition

    @staticmethod
    def noEmotionTrigger(mgr, input):
        if mgr.services.get("emotion"):
            # TODO: add emotion filter
            if mgr.services["emotion"]["state"] == State.EMOTION_NO:
                return True
        return False

    @staticmethod
    def newSoundTrigger(mgr, input):
        if mgr.services.get("sound"):
            if mgr.services["sound"]["state"] == State.SOUND_NEW:
                return True
        return False

    @staticmethod
    def availableSoundTrigger(mgr, input):
        if mgr.services.get("sound"):
            if mgr.services["sound"]["state"] == State.SOUND_AVAILABLE or mgr.services["sound"]["state"] == State.SOUND_NEW:
                return True
        return False

    @staticmethod
    def newConverseTrigger(mgr, input):
        newCondition = False
        intentCondition = False
        if mgr.services.get("converse"):
            # Check new/available condition
            newParameter = input["parameters"].get("new")
            if newParameter is None or newParameter:
                if mgr.services["converse"]["state"] == State.CONVERSE_NEW:
                    newCondition = True
            elif mgr.services["converse"]["state"] == State.CONVERSE_NEW or mgr.services["converse"]["state"] == State.CONVERSE_AVAILABLE:
                newCondition = True
            if input["parameters"].get("intent"):
                if mgr.services["converse"].get("intent"):
                    if mgr.services["converse"]["intent"] == input["parameters"]["intent"]:
                        intentCondition = True
            else:
                intentCondition = True
        return newCondition and intentCondition

mgr_triggers = Triggers()
