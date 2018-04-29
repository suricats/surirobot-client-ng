from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.Qt import QImage
import cv2
import time
import logging
import os
import re
import platform
from surirobot.core import ui


class VideoCapture(QThread):
    NB_IMG_PER_SECOND = 20
    signal_change_camera = pyqtSignal(QImage)

    def __init__(self):
        QThread.__init__(self)

        self.last_frame = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.signal_change_camera.connect(ui.setCamera)

    def __del__(self):
        cv2.destroyAllWindows()
        self.quit()

    def run(self):
        if platform.system() == "Darwin":
            video_capture = cv2.VideoCapture(0)
        else:
            # Get the devices
            try:
                fileList = os.listdir('/dev')
                regex = re.compile(r'^video')
                deviceList = list(filter(regex.match, fileList))
                # video_capture = cv2.VideoCapture(len(deviceList))
                video_capture = cv2.VideoCapture(len(deviceList)-1)
            except Exception as e:
                video_capture = cv2.VideoCapture(-1)

        if not video_capture.isOpened():
            print('Error - Can\'t open camera')
        while(True):
            try:
                time.sleep(-time.time() % (1 / self.NB_IMG_PER_SECOND))
                ret, frame = video_capture.read()
                self.last_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # cv2.imshow("preview", self.last_frame)
                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                self.signal_change_camera.emit(qImg)
            except Exception as e:
                print('Error : ' + str(e))
        video_capture.release()

    def get_frame(self):
        return self.last_frame
