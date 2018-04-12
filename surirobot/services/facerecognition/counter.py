from PyQt5.QtCore import QObject, pyqtSignal


class Counter(QObject):
    timeout = pyqtSignal()

    def __init__(self, interval):
        QObject.__init__(self)

        self.interval = interval
        self.count = 0
        self.active = False

    def increment(self):
        if self.active:
            self.count = self.count + 1

            if self.count >= self.interval:
                self.timeout.emit()
                self.stop()

    def start(self):
        self.reset()
        self.active = True

    def stop(self):
        self.reset()
        self.active = False

    def reset(self):
        self.count = 0

    def is_active(self):
        return self.active
