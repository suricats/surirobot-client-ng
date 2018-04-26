from PyQt5.QtGui import QFont, QPixmap, QImage, QPalette, QColor, QIcon

from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QMainWindow, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSlot, pyqtSignal
from .new import Ui_MainWindow
from surirobot.core.common import State


class MainWindow(QMainWindow, Ui_MainWindow):
    IMAGES_DIR = 'res/surifaces'
    IMAGES_EXT = ".jpg"
    MICRO_IMAGE = 'res/mic.png'

    SURI_BASIC = 0
    SURI_LISTENING = 1

    updateState = pyqtSignal(str, int, dict)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.setupUi(self)

        self.image.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setImage("basic")
        # Signals
        self.activateManualButton.clicked.connect(self.setManualInput)
        self.validateButton.clicked.connect(self.onClickValidateManualInput)
        # Font
        f = QFont('Roboto', 12, QFont.Bold)

        # Text Up
        self.labelUp.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelUp.setFont(f)
        self.labelUp.setText(".")

        # Text Middle
        self.labelMiddle.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelMiddle.setFont(f)
        self.labelMiddle.setText(".")

        # Text Down
        self.labelDown.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelDown.setFont(f)
        self.labelDown.setText(".")

        # Background color
        pal = QPalette()

        # set white background
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        # Others parameters
        self.activateManualButton.hide()
        self.manualLayoutContainer.hide()

    def load_image(self, image_path):
        image = QImage()
        print('image_path :' + str(image_path))
        image.load(image_path)
        return image

    # def smartShow(self):
    #     self.showFullScreen()
    #     self.updateWidgets()
    #     # Timer display fixer
    #     displayFixer = QTimer(self)
    #     displayFixer.setInterval(1000)
    #     displayFixer.setSingleShot(True)
    #     displayFixer.timeout.connect(self.updateWidgets)
    #     displayFixer.start()

    @pyqtSlot(str)
    def setTextUp(self, text):
        self.labelUp.setText(text)
        self.labelUp.adjustSize()

    @pyqtSlot(str)
    def setTextMiddle(self, text):
        self.labelMiddle.setText(text)
        self.labelMiddle.adjustSize()

    @pyqtSlot(str)
    def setTextDown(self, text):
        self.labelDown.setText(text)
        self.labelDown.adjustSize()

    @pyqtSlot(str)
    def setImage(self, image_id):
        try:
            image = self.load_image(self.IMAGES_DIR + '/' + image_id + self.IMAGES_EXT)
            self.image.setPixmap(QPixmap.fromImage(image).scaled(self.imageWidget.width(), self.imageWidget.height(), Qt.KeepAspectRatio))
        except Exception as e:
            print('Error while opening image :' + str(e))

    @pyqtSlot(QImage)
    def setCamera(self, qImg):
        self.camera.setPixmap(QPixmap.fromImage(qImg).scaled(self.cameraFrame.width(), self.cameraFrame.height(), Qt.KeepAspectRatio))

    @pyqtSlot()
    def setManualInput(self):
            self.manualLayoutContainer.show()

    @pyqtSlot()
    def onClickValidateManualInput(self):
        self.updateState.emit("keyboard", State.STATE_KEYBOARD_NEW, {"text": self.manualEdit.displayText()})
    # @pyqtSlot()
    # def updateWidgets(self):
    #     self.labelTextUp.adjustSize()
    #     self.labelTextMiddle.adjustSize()
    #     self.labelTextDown.adjustSize()
    #
    #     self.labelTextUp.move(
    #         self.width() / 2 - self.labelTextUp.width() / 2,
    #         self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2
    #     )
    #     self.labelTextMiddle.move(
    #         self.width() / 2 - self.labelTextUp.width() / 2,
    #         self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2 + self.labelTextUp.height()
    #     )
    #     self.labelTextDown.move(
    #         self.width() / 2 - self.labelTextUp.width() / 2,
    #         self.height() / 3 - self.labelTextUp.height() / 2 + self.imgWidget.height() / 2 + self.labelTextUp.height() + self.labelTextMiddle.height()
    #     )
    #
    #     self.imgWidget.adjustSize()
    #     self.imgWidget.move(
    #         self.width() / 2 - self.imgWidget.width() / 2,
    #         self.height() / 3 - self.imgWidget.height() / 2
    #     )

    # SIGNALS
    #
    # def setTextUpSignal(self, text):
    #     self.setTextUp(text)
    #
    # def setTextMiddleSignal(self, text):
    #     self.setTextMiddle(text)
    #
    # def setTextDownSignal(self, text):
    #     self.setTextDown(text)

    # Slots

    #def createManualWindow(self):
    #    manualW = manualWindow()
    #    manualW.show()
