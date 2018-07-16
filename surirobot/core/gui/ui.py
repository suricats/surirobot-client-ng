from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage, QPalette
from PyQt5.QtWidgets import QMainWindow

from surirobot.core.common import State, ehpyqtSlot
from .mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    SURIFACES_DIR = 'res/surifaces'
    INDICATORS_DIR = 'res/indicators'
    JPG = ".jpg"
    PNG = ".png"
    MICRO_IMAGE = 'res/mic.png'

    SURI_BASIC = 0
    SURI_LISTENING = 1

    update_state = pyqtSignal(str, int, dict)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.setupUi(self)

        self.set_image("basic")
        # Signals
        self.activateManualButton.clicked.connect(self.set_manual_input)
        self.validateButton.clicked.connect(self.on_click_validate_manual_input)
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

        self.knowProgressBar.hide()
        self.knowProgressText.hide()
        self.unknowProgressBar.hide()
        self.unknowProgressText.hide()
        self.nobodyProgressBar.hide()
        self.nobodyProgressText.hide()

        # Others parameters
        self.activateManualButton.hide()
        self.manualLayoutContainer.hide()

    def load_image(self, image_path):
        image = QImage()
        # print('image_path :' + str(image_path))
        image.load(image_path)
        return image

    @ehpyqtSlot(str)
    def set_text_up(self, text):
        self.labelUp.setText(text)
        self.labelUp.adjustSize()

    @ehpyqtSlot(str)
    def set_text_middle(self, text):
        self.labelMiddle.setText(text)
        self.labelMiddle.adjustSize()

    @ehpyqtSlot(str)
    def set_text_down(self, text):
        self.labelDown.setText(text)
        self.labelDown.adjustSize()

    @ehpyqtSlot(str)
    def set_image(self, image_id):
        try:
            image = self.load_image(self.SURIFACES_DIR + '/' + image_id + self.JPG)
            self.image.setPixmap(QPixmap.fromImage(image).scaled(self.imageWidget.width(), self.imageWidget.height(), Qt.KeepAspectRatio))
        except Exception as e:
            print('Error while opening image :' + str(e))

    @ehpyqtSlot(QImage)
    def set_camera(self, qImg):
        self.camera.setPixmap(QPixmap.fromImage(qImg).scaled(self.cameraFrame.width(), self.cameraFrame.height(), Qt.KeepAspectRatio))

    @ehpyqtSlot()
    def set_manual_input(self):
            self.manualLayoutContainer.show()

    @ehpyqtSlot()
    def on_click_validate_manual_input(self):
        self.update_state.emit("keyboard", State.KEYBOARD_NEW, {"text": self.manualEdit.displayText()})

    @ehpyqtSlot(str, str)
    def change_indicator(self, service, value):
        image = self.load_image(self.INDICATORS_DIR + '/' + service + '/' + value + self.PNG)
        if not image.isNull():
            if service == "face":
                self.faceIndicator.setPixmap(QPixmap.fromImage(image))
            elif service == "converse":
                self.converseIndicator.setPixmap(QPixmap.fromImage(image))
            elif service == "emotion":
                self.emotionIndicator.setPixmap(QPixmap.fromImage(image))
            else:
                print('Error - change_indicator : Service unknown')
        else:
            print('Error - change_indicator : Image can\'t be found')
    # @ehpyqtSlot()
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
