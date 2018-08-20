import logging

from PyQt5.QtCore import QObject, QTimer, QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication

from surirobot.core.common import ehpyqtSlot
from surirobot.devices import serv_ar


class KeyPressEventHandler(QObject):
    startRecord = pyqtSignal()
    stopRecord = pyqtSignal()

    take_picture = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.logger = logging.getLogger(type(self).__name__)
        self.onScenario = False
        self.audioRecording = False

        self.expirationTimer = QTimer()
        self.expirationTimer.setInterval(500)
        self.expirationTimer.setSingleShot(True)

        self.yoloTimer = QTimer()
        self.yoloTimer.setInterval(500)
        self.yoloTimer.setSingleShot(True)

        self.expirationTimer.timeout.connect(serv_ar.stop_record)
        # serv_ar.started_record.connect(self.manageRecord)
        self.startRecord.connect(serv_ar.start_record)

        # self.yoloTimer.timeout.connect(face_loader.take_picture_new_user)
        # self.take_picture.connect(face_loader.take_picture_new_user)

    # Communication between 2 different threads
    @ehpyqtSlot(bool)
    def manageRecord(self, val):
        self.audioRecording = val

    def eventFilter(self, obj, event):
        # Key pressed
        if event.type() == QEvent.KeyPress:
            key_p = event
            if (key_p.key() == Qt.Key_Escape) or (key_p.key() == Qt.Key_Return):
                self.logger.info('Leaving app...')
                QApplication.quit()
            elif key_p.key() == Qt.Key_C:
                # Expiration timer is set to prevent keyboard error
                if self.expirationTimer.isActive():
                    self.expirationTimer.stop()
                if not serv_ar.is_recording():
                    self.startRecord.emit()
                return True
            elif key_p.key() == Qt.Key_B:
                # Expiration timer is set to prevent keyboard error
                if self.yoloTimer.isActive():
                    self.yoloTimer.stop()
                return True
            else:
                return QObject.eventFilter(self, obj, event)

        # Key released
        elif event.type() == QEvent.KeyRelease:
            key_r = event
            if (key_r.key() == Qt.Key_C) and (not self.expirationTimer.isActive()):
                self.expirationTimer.start()
                return True
            if (key_r.key() == Qt.Key_B) and (not self.yoloTimer.isActive()):
                # self.take_picture.emit()
                self.yoloTimer.start()
                return True
        return QObject.eventFilter(self, obj, event)
