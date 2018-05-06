#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
rm -rf ${DIR}/build
rm -rf ${DIR}/dist
pyinstaller start.spec
mkdir ${DIR}/dist/surirobot/face_recognition_models
cp -rf ${DIR}/../face_recognition_models/models ${DIR}/dist/surirobot/face_recognition_models/models
cp -rf res ${DIR}/dist/surirobot/
cp -rf data ${DIR}/dist/surirobot/
mkdir ${DIR}/dist/surirobot/tmp
cp -rf scenario.json ${DIR}/dist/surirobot/scenario.json
cp -rf .env ${DIR}/dist/surirobot/.env
chmod +x ${DIR}/dist/surirobot/surirobot.elf
