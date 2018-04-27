#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pyinstaller start.py
cp -rf /usr/local/lib/python3.5/dist-packages/face_recognition_models ${DIR}/dist/start/
cp -rf res ${DIR}/dist/start/
cp -rf data ${DIR}/dist/start/
mkdir ${DIR}/dist/start/tmp
cp -rf scenario.json ${DIR}/dist/start/scenario.json
cp -rf .env ${DIR}/dist/start/.env
