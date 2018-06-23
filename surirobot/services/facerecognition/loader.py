from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import queue
import uuid
import shutil
from surirobot.services import serv_fr, serv_vc
from surirobot.core.common import Dir
import cv2
import os
import requests


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
            picture = self.q.get()
            serv_fr.addPicture(picture)

    def load_from_db(self):
        try:
            self.logger.info("Start loading faces ....")
            r1 = requests.get(self.url + '/memorize/users/', headers=self.headers)
            users = r1.json()["results"]
            for user in users:
                r2 = requests.get(self.url + '/memorize/users/' + str(user.get("id")) + '/pictures', headers=self.headers)
                pictures = r2.json()
                if pictures:
                    picture = pictures[0]
                    picture["user"] = user
                    # name = user.firstname + ' ' + user.lastname
                    # self.logger.info("Load Face {}".format(name))
                    serv_fr.addPicture(picture)
                    self.signalIndicator.emit("face", "orange")
        except Exception as e:
            print("load from db : " + str(e))

    def add_user(self, firstname, lastname, email, picture_path):
        r1 = requests.post(self.url + '/memorize/users/', {"firstname": firstname, "lastname": lastname, "email": email}, headers=self.headers)
        user = r1.json()
        new_path = Dir.PICTURES + format(uuid.uuid4()) + '.jpg'
        shutil.copy(picture_path, new_path)
        r2 = requests.post(self.url + '/memorize/pictures/', {"path": new_path, "user_id": user["id"]}, headers=self.headers)
        picture = r2.json()
        picture['user'] = user
        self.q.put(picture)

    @pyqtSlot(str, str)
    def take_picture_new_user(self, firstname, lastname):
        try:
            print("take_picture_new_user")
            picture = serv_vc.get_frame()
            file_path = Dir.TMP + format(uuid.uuid4()) + '.jpeg'
            cv2.imwrite(file_path, picture)
            self.new_user.emit(firstname)
            self.add_user(firstname, lastname, '', file_path)
        except Exception as e:
            print(e)
