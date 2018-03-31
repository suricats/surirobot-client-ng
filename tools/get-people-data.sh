#!/usr/bin/env bash

. $(dirname "$0")/../.env

curl --user ${REMOTE_DATA_LOGIN}:${REMOTE_DATA_PASSWD} https://suri.customer.berdy.pro/surirobot.db -o data/surirobot.db
curl --user ${REMOTE_DATA_LOGIN}:${REMOTE_DATA_PASSWD} https://suri.customer.berdy.pro/people-face.tar.gz -o people-face.tar.gz
tar -xvf people-face.tar.gz -C data && rm people-face.tar.gz
