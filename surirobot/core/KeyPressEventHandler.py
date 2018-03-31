from PyQt5.QtCore import QObject, QTimer, QEvent, Qt
from PyQt5.QtWidgets import QApplication


class KeyPressEventHandler(QObject):
    def __init__(self):
        self.onScenario = False
        self.audioRecording = False

        ### cm = converseManager::getInstance()
        ### sr = cm->getAudioRecorder()

        self.expirationTimer = QTimer()
        self.expirationTimer.setInterval(500)
        self.expirationTimer.setSingleShot(True)

        ### QObject.connect(expirationTimer,SIGNAL(timeout()),sr,SLOT(saveBuffer()));
        ### QObject.connect(sr,SIGNAL(isRecording(bool)),this,SLOT(manageRecord(bool)));
        ### QObject.connect(this,SIGNAL(startRecord()),sr,SLOT(recordInBuffer()));

    # Communication between 2 different threads
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
                if(not self.audioRecording):
                    ### emit startRecord()
                    pass
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
