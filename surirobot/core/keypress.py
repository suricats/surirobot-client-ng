from PyQt5.QtCore import QObject, QTimer, QEvent, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication
from surirobot.services import serv_ar


class KeyPressEventHandler(QObject):
    startRecord = pyqtSignal()
    stopRecord = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.onScenario = False
        self.audioRecording = False

        self.expirationTimer = QTimer()
        self.expirationTimer.setInterval(500)
        self.expirationTimer.setSingleShot(True)

        self.expirationTimer.timeout.connect(serv_ar.stop_record)
        #serv_ar.started_record.connect(self.manageRecord)
        self.startRecord.connect(serv_ar.start_record)

    # Communication between 2 different threads
    @pyqtSlot(bool)
    def manageRecord(self, val):
        self.audioRecording = val

    def eventFilter(self, obj, event):
        # Key pressed
        if(event.type() == QEvent.KeyPress):
            keyP = event
            if((keyP.key() == Qt.Key_Escape) or (keyP.key() == Qt.Key_Return)):
                QApplication.quit()
            elif(keyP.key() == Qt.Key_C):
                # Expiration timer is set to prevent keyboard error
                if(self.expirationTimer.isActive()):
                    self.expirationTimer.stop()
                if(not serv_ar.is_recording()):
                    self.startRecord.emit()
                return True
            else:
                return QObject.eventFilter(obj, event)

        # Key released
        elif(event.type() == QEvent.KeyRelease):
            keyR = event
            if((keyR.key() == Qt.Key_C) and (not self.expirationTimer.isActive())):
                self.expirationTimer.start()
                return True
        return QObject.eventFilter(obj, event)
