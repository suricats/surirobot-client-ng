from PyQt5.QtCore import QThread
import logging
from surirobot.management.mod_api.models import User
from surirobot.core import serv_fr


class FaceLoader(QThread):
    def __init__(self):
        QThread.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Start loading faces ....")

        users = User.query.all()

        for user in users:
            pictures = user.pictures
            if pictures:
                picture = pictures[0]

                name = user.firstname + ' ' + user.lastname
                self.logger.info("Load Face  ..... {}".format(name))
                serv_fr.add_picture(picture)

    def __del__(self):
        self.wait()
