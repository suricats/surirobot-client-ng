from .base import ApiCaller
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QUrl, pyqtSlot, pyqtSignal


class EmotionalAPICaller(ApiCaller):
    new_file = pyqtSignal('QByteArray')

    def __init__(self, text):
        ApiCaller.__init__(self, text)

    def __del__(self):
        self.stop()

    @pyqtSlot('QNetworkReply*')
    def receiveReply(self, reply):
        self.isBusy = False
        data = reply.readAll()
        self.new_file.emit(data)
        reply.deleteLater()

    @pyqtSlot(str)
    def sendRequest(self, urlStr):
        url = QUrl.fromUserInput(urlStr)
        parsedUrl = QUrl(url)
        request = QNetworkRequest(parsedUrl)
        self.networkManager.get(request)

    EmotionalAPICaller::EmotionalAPICaller(QString text) :
    APICaller(text) {
        if (!cap.open(-1)) std::cerr << "Error - No camera found" << std::endl;
        captureTimer = new QTimer();
        requestTimer = new QTimer();
        //Set the capture timer (every 3 seconds)
        captureTimer->setInterval(200);
        requestTimer->setInterval(EMOTIONAL_DELAY);
        QObject::connect(captureTimer, SIGNAL(timeout()), this, SLOT(captureImage()));
        QObject::connect(requestTimer, SIGNAL(timeout()), this, SLOT(sendRequest()));
    }

    def receiveReply(self, reply):
        if (reply.error() != QNetworkReply.NoError):
            print("Error " + reply.error())
            std::cerr << reply->readAll().toStdString() << std::endl;
            networkManager->clearAccessCache();
        } else {
            QJsonObject jsonObject = QJsonDocument::fromJson(reply->readAll()).object();
            QJsonArray tmpAr = jsonObject["facial"].toArray();
            QString message = "Emotions : ";
            for (QJsonValue val : tmpAr) {
                message += val.toObject()["emotion"].toString("?");
                message += ",";
            }
            emit newReply(message);


        }
        isBusy = false;
        reply->deleteLater();
    }

    void EmotionalAPICaller::captureImage() {
        cap >> currentFrame;
        cv::resize(currentFrame, currentFrame, cv::Size(EMOTIONAL_IMAGE_SIZE, EMOTIONAL_IMAGE_SIZE));
        std::string a = "Camera n°1";
        cv::imshow(a, currentFrame);
    }

    void EmotionalAPICaller::start() const {
        APICaller::start();
        captureTimer->start();
        requestTimer->start();

    }

    void EmotionalAPICaller::sendRequest(QString text) {
        isBusy = true;
        //Get base64 string from cv::mat
        std::string ext = "jpeg";
        std::vector<uint8_t> buffer;
        cv::imencode("." + ext, currentFrame, buffer);
        QByteArray byteArray = QByteArray::fromRawData((const char*) buffer.data(), buffer.size());
        QString base64Image(byteArray.toBase64());

        //Prepare request
        QJsonObject jsonObject;
        jsonObject["pictures"] = base64Image;
        QJsonDocument jsonData(jsonObject);
        QByteArray data = jsonData.toJson();
        QNetworkRequest request(url);
        //std::cout << "Sended to Emotional API : " << data.toStdString().substr(0,30) << "..." << std::endl;
        request.setHeader(QNetworkRequest::ContentTypeHeader, QVariant("application/json"));
        networkManager->post(request, data);
    }
