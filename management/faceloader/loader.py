import logging

from management.mod_api.models import User
from recognition_engine.utils import add_picture


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

            add_picture(picture)
