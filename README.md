# HAL-1 v1.2

Client part of the HAL-1 (ex Surirobot) , a multi-users smart assistant.
Works on Python 3.6

## Installation under macOS using homebrew

Install homebrew : https://brew.sh

Install libs: `brew install python3 boost-python3 dlib espeak cmake mysql`

Install required python3 modules: `pip3 install -r requirements.txt`

Install the lastest version of python3 dlib:

```bash
git clone https://github.com/davisking/dlib.git
cd dlib
python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA
cd .. && rm -rf dlib
```
Create a symlink on libespeak.dylib :
`cd /usr/local/lib/ && ln -s libespeak.dylib libespeak.so.1`

## Installation under ubuntu

```bash
sudo apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    virtualenv \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    python3-setuptools \
    python3-pip \
    software-properties-common \
    zip \
    libasound2-dev \
    sshpass
```

Install required python3 modules: `pip3 install -r requirements.txt`

For Ubuntu 18 (not supported)
- change libatlas-dev by libatlas-base-dev
- add portaudio19-dev
- If you have issues with HTTPS request see : https://stackoverflow.com/questions/50201988/pyqt5-ubuntu-18-04-error-99-on-qnetworkreply-when-request-to-https-url/50720834#50720834

Install the lastest version of python3 dlib:

```bash
git clone https://github.com/davisking/dlib.git
cd dlib
python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA
cd .. && rm -rf dlib
```
## Configure the environment file
* Configure .env 
```shell
cp .env.example .env
```
If you want to use the default environment
- Fill only the ```REMOTE_DATA_LOGIN```  and ```REMOTE_DATA_PASSWD``` fields
- Run the command : ```tools/get-env```

## Launch the program 

* Clone repository 
* Create virtualenv
* If you have some trouble with the command ```workon``` see : https://stackoverflow.com/questions/29900090/virtualenv-workon-doesnt-work
```shell
mkvirtualenv surirobot && workon surirobot
```

* Install dependencies
```shell
pip install -r requirements.txt
```

* Run the program
```shell
python start.py
```


## TODO
WIP
## CHANGELOG
WIP
