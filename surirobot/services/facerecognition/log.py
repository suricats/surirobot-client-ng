from PyQt5.QtCore import QObject, pyqtSlot
from surirobot.core.common import ehpyqtSlot
import logging
# from surirobot.management.mod_api.models import LogRecognize
# from surirobot.management import db


class FaceLogger(QObject):
    def __init__(self):
        QObject.__init__(self)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @ehpyqtSlot(bool)
    def log(self, value):
        pass
        # log = LogRecognize(value=value)

        # db.session.add(log)
        # db.session.commit()

    def __del__(self):
        self.quit()
