from .keypress import KeyPressEventHandler
from surirobot.core import ui

keyboard = KeyPressEventHandler()
ui.installEventFilter(keyboard)
