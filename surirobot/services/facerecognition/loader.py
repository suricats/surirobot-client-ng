from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import queue
import uuid
from surirobot.services import serv_fr, serv_vc
from surirobot.core.common import Dir
import cv2
import os
import requests
import face_recognition


class FaceLoader(QThread):
    signalIndicator = pyqtSignal(str, str)
    new_user = pyqtSignal(str)
    token = os.environ.get('API_MEMORY_TOKEN', '')
    url = os.environ.get('API_MEMORY_URL', '')
    headers = {'Authorization': 'Token ' + token}

    def __init__(self):
        QThread.__init__(self)

        self.q = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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
            r1 = requests.get(self.url + '/memorize/users/', headers=self.headers)
            # print(r1.json())
            users = r1.json()
            for user in users:
                r2 = requests.get(self.url + '/memorize/users/' + str(user.get("id")) + '/encodings/', headers=self.headers)
                models = r2.json()
                for model in models:
                    counter += 1
                    model["user"] = user
                    # name = user.firstname + ' ' + user.lastname
                    # self.logger.info("Load Face {}".format(name))
                    serv_fr.addModel(model)
                    self.signalIndicator.emit("face", "orange")
            self.logger.info(str(counter) + " model(s) loaded !")
        except Exception as e:
            print("load from db : " + str(e))

    def add_user(self, firstname, lastname, email, face):
        r1 = requests.post(self.url + '/memorize/users/', {"firstname": firstname, "lastname": lastname, "email": email}, headers=self.headers)
        user = r1.json()
        r2 = requests.post(self.url + '/memorize/pictures/', {"path": " ".join(map(str, face)), "user_id": user["id"]}, headers=self.headers)
        model = r2.json()
        # model["path"] = list(model["path"])
        model['user'] = user
        self.q.put(model)

    @pyqtSlot(str, str)
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
            print("take_picture : " + str(e))
