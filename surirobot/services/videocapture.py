from PyQt5.QtCore import QThread
import cv2
import time
import logging


class VideoCapture(QThread):
    NB_IMG_PER_SECOND = 4

    def __init__(self):
        QThread.__init__(self)

        self.last_frame = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        self.wait()

    def run(self):
        video_capture = cv2.VideoCapture(0)

        while(True):
            time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
            ret, frame = video_capture.read()
            self.last_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        video_capture.release()

    def get_frame(self):
        return self.last_frame
