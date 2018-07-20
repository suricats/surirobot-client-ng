from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage, QPalette
from PyQt5.QtWidgets import QMainWindow

from surirobot.core.common import State, ehpyqtSlot
from .mainwindow import Ui_MainWindow
import logging


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
        self.logger = logging.getLogger(type(self).__name__)

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
        """
        Change the text in the upper box

        Parameters
        ----------
        text : str
            New text
        """
        self.labelUp.setText(text)
        self.labelUp.adjustSize()

    @ehpyqtSlot(str)
    def set_text_middle(self, text):
        """
        Change the text in the middle box

        Parameters
        ----------
        text : str
            New text
        """
        self.labelMiddle.setText(text)
        self.labelMiddle.adjustSize()

    @ehpyqtSlot(str)
    def set_text_down(self, text):
        """
        Change the text in the lower box

        Parameters
        ----------
        text : str
            New text
        """
        self.labelDown.setText(text)
        self.labelDown.adjustSize()

    @ehpyqtSlot(str)
    def set_image(self, image_id):
        """
        Change the image of the avatar

        Parameters
        ----------
        image_id : str
            ID of the image
        """

        image = self.load_image(self.SURIFACES_DIR + '/' + image_id + self.JPG)  # type: QImage
        self.image.setPixmap(QPixmap.fromImage(image).scaled(self.imageWidget.width(), self.imageWidget.height(), Qt.KeepAspectRatio))


    @ehpyqtSlot(QImage)
    def set_camera(self, q_img):
        """
        Change the image of the camera

        Parameters
        ----------
        q_img : QImage
            ID of the image
        """
        #self.logger.debug('q_img:{},{}'.format(type(q_img).__name__, q_img.byteCount()))
        try:
            self.camera.setPixmap(QPixmap.fromImage(q_img).scaled(self.cameraFrame.width(), self.cameraFrame.height(), Qt.KeepAspectRatio))
        except Exception as e:
            self.logger.error('{} occurred while setting camera\n{}'.format(type(e).__name__, e))

    @ehpyqtSlot()
    def set_manual_input(self, checked):
        """
        Activate the manual layout
        """
        self.manualLayoutContainer.show()

    @ehpyqtSlot()
    def on_click_validate_manual_input(self, checked):
        """
        Send a signal to manager

        Returns
        ----------
        None:
            This function send a signal
        """
        self.update_state.emit("keyboard", State.KEYBOARD_NEW, {"text": self.manualEdit.displayText()})

    @ehpyqtSlot(str, str)
    def change_indicator(self, service, value):
        """
        Change the image of the indicator

        Parameters
        ----------
        service : str
            Name of the service
        value : str
            Value of the indicator
        """
        image = self.load_image(self.INDICATORS_DIR + '/' + service + '/' + value + self.PNG)
        if not image.isNull():
            if service == "face":
                self.faceIndicator.setPixmap(QPixmap.fromImage(image))
            elif service == "converse":
                self.converseIndicator.setPixmap(QPixmap.fromImage(image))
            elif service == "emotion":
                self.emotionIndicator.setPixmap(QPixmap.fromImage(image))
            else:
                raise Exception("change_indicator : Service unknown")
        else:
            raise Exception("change_indicator : Image can't be found")

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
