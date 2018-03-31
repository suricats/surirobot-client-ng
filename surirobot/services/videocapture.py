from threading import Thread, Event
import cv2
import time
import logging


class VideoCapture(Thread):
    NB_IMG_PER_SECOND = 1

    def __init__(self):
        Thread.__init__(self)
        self._stop_event = Event()

        self.last_frame = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self):
        video_capture = cv2.VideoCapture(0)

        while(not self._stop_event.is_set()):
            time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
            ret, frame = video_capture.read()
            self.last_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        video_capture.release()

    def get_frame(self):
        return self.last_frame

    def stop(self):
        self._stop_event.set()
