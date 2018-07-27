from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import queue
import uuid
from surirobot.services import serv_fr
from surirobot.devices import serv_vc
from surirobot.core.api import api_memory
from surirobot.core.common import Dir, ehpyqtSlot
import cv2
import os
import requests
import face_recognition
import traceback

class FaceLoader(QThread):
    signal_indicator = pyqtSignal(str, str)
    new_user = pyqtSignal(str)
    token = os.environ.get('API_MEMORY_TOKEN', '')
    url = os.environ.get('API_MEMORY_URL', '')
    headers = {'Authorization': 'Token ' + token}

    def __init__(self):
        QThread.__init__(self)

        self.q = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(type(self).__name__)

    def __del__(self):
        self.quit()

    def run(self):
        self.load_from_db()

        while True:
            model = self.q.get()
            serv_fr.addModel(model)

    def load_from_db(self):
        try:
            counter = 0
            self.logger.info("Start loading models ....")
            self.signal_indicator.emit("face", "orange")
            users = api_memory.get_users()
            for user in users:
                models = api_memory.get_encodings(user.get("id"))
                for model in models:
                    counter += 1
                    model["user"] = user
                    # name = user.firstname + ' ' + user.lastname
                    # self.logger.info("Load Face {}".format(name))
                    serv_fr.addModel(model)
            self.logger.info(str(counter) + " model(s) loaded !")
            self.signal_indicator.emit("face", "green")
        except Exception as e:
            self.logger.error("{} occurred while loading encodings.\n{}.".format(type(e).__name__, e))
            traceback.print_exc()
            self.signal_indicator.emit("face", "red")

    def add_user(self, firstname, lastname, email, face):
        try:
            user = api_memory.add_user(firstname, lastname, email)
            model = api_memory.add_encoding(face, user['id'])
            model['user'] = user
            self.q.put(model)
        except Exception as e:
            self.logger.error("{} occurred while adding user.\n{}.".format(type(e).__name__, e))
            traceback.print_exc()
            self.signal_indicator.emit("face", "orange")

    @ehpyqtSlot(str, str)
    def take_picture_new_user(self, firstname, lastname):
        try:
            picture = serv_vc.get_frame()
            file_path = Dir.TMP + format(uuid.uuid4()) + '.jpeg'
            cv2.imwrite(file_path, picture)
            img = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(img, None, 10)
            if encodings:
                face = encodings[0]
            else:
                self.logger.info('No face on the model')
                face = None
            self.new_user.emit(firstname)
            self.add_user(firstname, lastname, '', face)
        except Exception as e:
            self.logger.error("{} occurred while creating picture for new user\n{}".format(type(e).__name__, e))
            traceback.print_exc()
