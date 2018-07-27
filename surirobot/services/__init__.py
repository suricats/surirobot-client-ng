from PyQt5.QtCore import QThread


# Start FaceRecognition
from surirobot.services.facerecognition import FaceRecognition
serv_fr = FaceRecognition()
serv_fr.start()

# Load faces from DB
from surirobot.services.facerecognition.loader import FaceLoader
face_loader = FaceLoader()
face_loader.start(QThread.LowestPriority)

# Start EmotionalRecognition
from surirobot.services.emotional import EmotionalRecognition
serv_emo = EmotionalRecognition()
serv_emo.start()

# Start Keyboard listener
from surirobot.services.keyboard import KeyPressEventHandler
from surirobot.core import ui

serv_keyboard = KeyPressEventHandler()
ui.installEventFilter(serv_keyboard)
