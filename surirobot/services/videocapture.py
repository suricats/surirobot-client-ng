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
    NB_IMG_PER_SECOND = 20
    signal_change_camera = pyqtSignal(QImage)

    def __init__(self):
        QThread.__init__(self)

        self.last_frame = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
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
                fileList = os.listdir('/dev')
                regex = re.compile(r'^video')
                deviceList = list(filter(regex.match, fileList))
                # video_capture = cv2.VideoCapture(len(deviceList))
                self.nbCam = len(deviceList)
                if self.nbCam <= 1:
                    ui.nextCamera.hide()
                self.currentCam = 0
                self.video_capture = cv2.VideoCapture(0)
            except Exception as e:
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
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
                self.signal_change_camera.emit(qImg)
        except Exception as e:
            print('Error : ' + str(e))
        self.videoWorkLoop.setInterval(-time.time() % (1 / self.NB_IMG_PER_SECOND)*1000)

    @ehpyqtSlot()
    def change_camera(self):
        self.currentCam = (self.currentCam+1) % self.nbCam
        self.video_capture.open(self.currentCam)

    def get_frame(self):
        return self.last_frame
