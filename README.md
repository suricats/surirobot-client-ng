# Surirobot [WIP]

Full client.

## Installation under macOS using homebrew

Install libs: `brew install python3 boost-python3 dlib cmake mysql`

Install required python3 modules: `pip3 install -r requirements.txt`

Install the lastest version of python3 dlib:

```bash
git clone https://github.com/davisking/dlib.git
cd dlib
python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA
cd .. && rm -rf dlib
```

## Installation under ubuntu

```bash
apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
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
    libasound2-dev
```

Install required python3 modules: `pip3 install -r requirements.txt`

For Ubuntu 18
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


## Get the suricats face pack

```bash
cp .env.example .env
nano .env
```

Fill the login & password fields

```bash
tools/get-people-data.sh
```

## Launch the program

`cd <project_dir>`

`python3 start.py`
