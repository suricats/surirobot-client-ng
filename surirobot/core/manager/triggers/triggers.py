from surirobot.core.common import State
import re
import logging

logger = logging.getLogger('Triggers')


class Triggers:

    def __init__(self):
        self.triggers = {}

    def generate_triggers(self, services):
        # Generate services domain for triggers
        for service in services:
            self.triggers[service] = {}

        # Register triggers
        self.triggers["sound"]["new"] = self.new_sound_trigger
        self.triggers["sound"]["available"] = self.available_sound_trigger

        self.triggers["converse"]["new"] = self.new_converse_trigger

        self.triggers["face"]["unknow"] = self.new_person_trigger
        self.triggers["face"]["know"] = self.know_person_trigger
        self.triggers["face"]["nobody"] = self.nobody_trigger
        self.triggers["face"]["several"] = self.several_person_trigger
        self.triggers["face"]["working"] = self.face_working

        self.triggers["emotion"]["new"] = self.new_emotion_trigger
        self.triggers["emotion"]["no"] = self.no_emotion_trigger

        self.triggers["keyboard"]["new"] = self.new_keyboard_params_trigger
        return self.triggers

    # Triggers
    @staticmethod
    def face_working(mgr, params):
        if not (params["parameters"].get("value") is None):
            if mgr.services.get("face"):
                if mgr.services["face"]["working"]:
                    return params["parameters"]["value"]
                else:
                    return not params["parameters"]["value"]
        return False

    @staticmethod
    def new_person_trigger(mgr, params):
        # TODO: add separation new/available with params["parameters"]["new"]
        if mgr.services.get("face"):
            if mgr.services["face"].get("state") is not None:
                if mgr.services["face"]["state"] == State.FACE_UNKNOWN:
                    return True
        return False

    @staticmethod
    def several_person_trigger(mgr, params):
        if mgr.services.get("face"):
            if mgr.services["face"].get("state") is not None:
                if mgr.services["face"]["state"] == State.FACE_MULTIPLES:
                    return True
        return False

    @staticmethod
    def know_person_trigger(mgr, params):
        # TODO: add separation new/available with params["parameters"]["new"]
        first_name_regex = True
        last_name_regex = True
        full_name_regex = True
        new_condition = False
        if mgr.services.get("face"):
            if mgr.services["face"].get("state") is not None:
                # Check new/available condition
                new_parameter = params["parameters"].get("new")
                if new_parameter is None or new_parameter:
                    if mgr.services["face"]["state"] == State.FACE_KNOWN:
                        new_condition = True
                elif mgr.services["face"]["state"] == State.FACE_KNOWN or mgr.services["face"]["state"] == State.FACE_KNOWN_AVAILABLE:
                    new_condition = True
                # Check if regex for name is activated
                if params["parameters"].get("name"):
                    pattern_name = re.compile(params["parameters"]["name"])
                    if not mgr.services["face"].get("name"):
                        full_name_regex = False
                    elif pattern_name.match(mgr.services["face"]["name"]):
                        full_name_regex = True
                    else:
                        full_name_regex = False

                # Check if regex for firstname is activated
                if params["parameters"].get("firstname"):
                    pattern_firstname = re.compile(params["parameters"]["firstname"])
                    if not mgr.services["face"].get("firstname"):
                        first_name_regex = False
                    elif pattern_firstname.match(mgr.services["face"]["firstname"]):
                        first_name_regex = True
                    else:
                        first_name_regex = False

                # Check if regex for lastname is activated
                if params["parameters"].get("lastname"):
                    pattern_lastname = re.compile(params["parameters"]["lastname"])
                    if not mgr.services["face"].get("lastname"):
                        last_name_regex = False
                    elif pattern_lastname.match(mgr.services["face"]["lastname"]):
                        last_name_regex = True
                    else:
                        last_name_regex = False
        # logger.debug('know_person_trigger : {},{},{},{}'.format(first_name_regex, last_name_regex, new_condition, full_name_regex))
        return first_name_regex and last_name_regex and new_condition and full_name_regex

    @staticmethod
    def nobody_trigger(mgr, params):
        if mgr.services.get("face"):
            # TODO: Implement regex parameters
            if mgr.services["face"].get("state") == State.FACE_NOBODY:
                return True
        return False

    @staticmethod
    def new_emotion_trigger(mgr, params):
        if mgr.services.get("emotion"):
            if mgr.services["emotion"]["state"] == State.EMOTION_NEW:
                if params["parameters"].get("emotion"):
                    if mgr.services["emotion"]["emotion"] == params["parameters"]["emotion"]:
                        return True
                    else:
                        return False
                else:
                    return True
        return False

    @staticmethod
    def new_keyboard_params_trigger(mgr, params):
        new_condition = False
        if mgr.services.get("keyboard"):
            # Check new/available condition
            new_parameter = params["parameters"].get("new")
            if new_parameter is None or new_parameter:
                if mgr.services["keyboard"]["state"] == State.KEYBOARD_NEW:
                    new_condition = True
            elif mgr.services["keyboard"]["state"] == State.KEYBOARD_AVAILABLE or mgr.services["keyboard"]["state"] == State.KEYBOARD_AVAILABLE:
                new_condition = True
        return new_condition

    @staticmethod
    def no_emotion_trigger(mgr, params):
        if mgr.services.get("emotion"):
            # TODO: add emotion filter
            if mgr.services["emotion"]["state"] == State.EMOTION_NO:
                return True
        return False

    @staticmethod
    def new_sound_trigger(mgr, params):
        if mgr.services.get("sound"):
            if mgr.services["sound"]["state"] == State.SOUND_NEW:
                return True
        return False

    @staticmethod
    def available_sound_trigger(mgr, params):
        if mgr.services.get("sound"):
            if mgr.services["sound"]["state"] == State.SOUND_AVAILABLE or mgr.services["sound"]["state"] == State.SOUND_NEW:
                return True
        return False

    @staticmethod
    def new_converse_trigger(mgr, params):
        new_condition = False
        intent_condition = False
        if mgr.services.get("converse"):
            # Check new/available condition

            new_parameter = params["parameters"].get("new")
            if new_parameter is None or new_parameter:
                if mgr.services["converse"]["state"] == State.CONVERSE_NEW:
                    new_condition = True
            elif mgr.services["converse"]["state"] == State.CONVERSE_NEW or mgr.services["converse"]["state"] == State.CONVERSE_AVAILABLE:
                new_condition = True
            if params["parameters"].get("intent"):
                if mgr.services["converse"].get("intent"):
                    if mgr.services["converse"]["intent"] == params["parameters"]["intent"]:
                        intent_condition = True
            else:
                intent_condition = True
        return new_condition and intent_condition


mgr_triggers = Triggers()
