from PyQt5.QtCore import QObject, QTimer, QEvent, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication
from surirobot.services import serv_ar, face_loader

class KeyPressEventHandler(QObject):
    startRecord = pyqtSignal()
    stopRecord = pyqtSignal()

    take_picture = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.onScenario = False
        self.audioRecording = False

        self.expirationTimer = QTimer()
        self.expirationTimer.setInterval(500)
        self.expirationTimer.setSingleShot(True)

        self.yoloTimer = QTimer()
        self.yoloTimer.setInterval(500)
        self.yoloTimer.setSingleShot(True)

        self.expirationTimer.timeout.connect(serv_ar.stop_record)
        #serv_ar.started_record.connect(self.manageRecord)
        self.startRecord.connect(serv_ar.start_record)

        # self.yoloTimer.timeout.connect(face_loader.take_picture_new_user)
        # self.take_picture.connect(face_loader.take_picture_new_user)

    # Communication between 2 different threads
    @pyqtSlot(bool)
    def manageRecord(self, val):
        self.audioRecording = val

    def eventFilter(self, obj, event):
        # Key pressed
        if(event.type() == QEvent.KeyPress):
            keyP = event
            if((keyP.key() == Qt.Key_Escape) or (keyP.key() == Qt.Key_Return)):
                print('Leaving app...')
                QApplication.quit()
            elif(keyP.key() == Qt.Key_C):
                # Expiration timer is set to prevent keyboard error
                if(self.expirationTimer.isActive()):
                    self.expirationTimer.stop()
                if(not serv_ar.is_recording()):
                    self.startRecord.emit()
                return True
            elif(keyP.key() == Qt.Key_B):
                # Expiration timer is set to prevent keyboard error
                if(self.yoloTimer.isActive()):
                    self.yoloTimer.stop()
                return True
            else:
                return QObject.eventFilter(self, obj, event)

        # Key released
        elif(event.type() == QEvent.KeyRelease):
            keyR = event
            if((keyR.key() == Qt.Key_C) and (not self.expirationTimer.isActive())):
                self.expirationTimer.start()
                return True
            if((keyR.key() == Qt.Key_B) and (not self.yoloTimer.isActive())):
                #self.take_picture.emit()
                self.yoloTimer.start()
                return True
        return QObject.eventFilter(self, obj, event)
