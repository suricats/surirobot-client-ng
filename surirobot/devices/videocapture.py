from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt5.Qt import QImage
import cv2
import time
import logging
import os
import re
import platform
from surirobot.core import ui
from surirobot.core.common import ehpyqtSlot


class VideoCapture(QThread):
    """
    Threaded service that records audio
    """
    NB_IMG_PER_SECOND = 15
    signal_change_camera = pyqtSignal(QImage)

    def __init__(self):
        QThread.__init__(self)

        self.last_frame = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(type(self).__name__)
        self.nbCam = 0
        self.currentCam = 0
        self.video_capture = None
        self.signal_change_camera.connect(ui.set_camera)
        ui.nextCamera.pressed.connect(self.change_camera)

        self.videoWorkLoop = QTimer()
        self.videoWorkLoop.timeout.connect(self.detect)
        self.videoWorkLoop.setInterval(1000/self.NB_IMG_PER_SECOND)

    def __del__(self):
        self.video_capture.release()
        cv2.destroyAllWindows()
        self.quit()

    def start(self, **kwargs):
        if platform.system() == "Darwin":
            self.video_capture = cv2.VideoCapture(0)
            self.nbCam = 1
            self.currentCam = 0
            ui.nextCamera.hide()
        else:
            # Get the devices
            try:
                file_list = os.listdir('/dev')
                regex = re.compile(r'^video')
                device_list = list(filter(regex.match, file_list))
                # video_capture = cv2.VideoCapture(len(device_list))
                self.nbCam = len(device_list)
                if self.nbCam <= 1:
                    ui.nextCamera.hide()
                self.currentCam = 0
                self.video_capture = cv2.VideoCapture(0)
            except Exception:
                self.video_capture = cv2.VideoCapture(-1)
        if self.video_capture.isOpened():
            self.videoWorkLoop.start()
        else:
            raise Exception("Can't open camera.")

    @ehpyqtSlot()
    def detect(self):
        try:
            ret, frame = self.video_capture.read()
            if frame is not None:
                self.last_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # cv2.imshow("preview", self.last_frame)
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.signal_change_camera.emit(q_img)
        except Exception as e:
            self.logger.error('{} occurred while detecting.\n{}'.format(type(e).__name__, e))
        self.videoWorkLoop.setInterval(-time.time() % (1 / self.NB_IMG_PER_SECOND)*1000)

    @ehpyqtSlot()
    def change_camera(self):
        self.currentCam = (self.currentCam+1) % self.nbCam
        self.video_capture.open(self.currentCam)

    def get_frame(self):
        return self.last_frame
