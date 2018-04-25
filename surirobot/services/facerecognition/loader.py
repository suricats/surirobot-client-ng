from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
import logging
import queue
import uuid
import shutil
from surirobot.management import db
from surirobot.management.mod_api.models import User, Picture
from surirobot.services import serv_fr, serv_vc
from surirobot.core.common import Dir
from random import randint
import cv2


class FaceLoader(QThread):
    new_user = pyqtSignal(str)

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
            serv_fr.add_picture(picture)

    def load_from_db(self):
        self.logger.info("Start loading faces ....")

        users = User.query.all()

        for user in users:
            pictures = user.pictures
            if pictures:
                picture = pictures[0]
                name = user.firstname + ' ' + user.lastname
                #self.logger.info("Load Face {}".format(name))
                serv_fr.add_picture(picture)
        self.logger.info('Loaded all the faces from DB')

    def add_user(self, firstname, lastname, email, picture_path):
        user = User(firstname=firstname, lastname=lastname, email=email)
        db.session.add(user)
        db.session.commit()
        new_path = Dir.PICTURES + format(uuid.uuid4()) + '.jpg'
        shutil.copy(picture_path, new_path)
        print(user.id)
        picture = Picture(path=new_path, user=user)
        db.session.add(picture)
        db.session.commit()

        self.q.put(picture)

    @pyqtSlot(str, str)
    def take_picture_new_user(self, firstname, lastname):
        picture = serv_vc.get_frame()
        file_path = Dir.TMP + format(uuid.uuid4()) + '.jpeg'
        cv2.imwrite(file_path, picture)
        self.new_user.emit(firstname)
        self.add_user(firstname, lastname, '', file_path)
