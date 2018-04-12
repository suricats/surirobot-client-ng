from PyQt5.QtCore import QThread
import logging
import queue
import uuid
import shutil
from surirobot.management import db
from surirobot.management.mod_api.models import User, Picture
from surirobot.services import serv_fr
from surirobot.core.common import Dir



class FaceLoader(QThread):
    def __init__(self):
        QThread.__init__(self)

        self.q = queue.Queue()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.wait()

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
        print(user.id)
        new_path = Dir.PICTURES + uuid.uuid4() + '.jpg'
        shutil.copy(picture_path, new_path)
        picture = Picture(path=new_path, user_id=user.id)
        #db.session.add(user)
        #db.session.add(picture)
        #db.session.commit()
        self.q.put(picture)
