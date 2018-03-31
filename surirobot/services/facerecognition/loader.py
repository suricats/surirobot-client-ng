import logging

from surirobot.management.mod_api.models import User
import shared as s


def load_faces():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Start loading faces ....")

    users = User.query.all()

    for user in users:
        pictures = user.pictures
        if pictures:
            picture = pictures[0]

            name = user.firstname + ' ' + user.lastname
            logger.info("Load Face  ..... {}".format(name))

            s.serv_fr.add_picture(picture)
