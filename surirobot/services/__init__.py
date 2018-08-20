import os

from PyQt5.QtCore import QThread


# Start FaceRecognition
from surirobot.core.api import URLNotDefinedAPIException
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

# Start Redis listener
url_redis = os.environ.get('REDIS_SERVER_URL')
if url_redis:
    from .redis import RedisService
    serv_redis = RedisService(url_redis)
    serv_redis.listen('slack')
else:
    raise URLNotDefinedAPIException('REDIS')