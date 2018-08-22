import logging
import os

import requests
from PyQt5.QtCore import pyqtSignal

from surirobot.core.common import ehpyqtSlot
from .base import ApiCaller


class MemoryApiCaller(ApiCaller):
    """
    API class for Memory API

    https://github.com/suricats/surirobot-api-memory
    """
    new_user = pyqtSignal(dict)
    new_encodings = pyqtSignal(list)
    new_encoding = pyqtSignal(dict)
    new_notifications = pyqtSignal(list)
    new_sensor_last = pyqtSignal(dict)
    new_sensors = pyqtSignal(list)
    notifications = pyqtSignal(dict)
    users_list = pyqtSignal(list)

    def __init__(self, url):
        ApiCaller.__init__(self, url)
        self.logger = logging.getLogger(type(self).__name__)
        token = os.environ.get('API_MEMORY_TOKEN', '')
        self.headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    def __del__(self):
        self.stop()

    def get_encodings(self, user_id):
        """
        Get encodings of specific user from the memory of the Surirobot

        Parameters
        ----------
        user_id : int
            id of user
        Returns
        -------
        dict
            This function send a dict containing the encodings
        """
        r = requests.get(self.url + '/api/memory/users/' + str(user_id) + '/encodings/', headers=self.headers)
        # Receive response
        if r.status_code == 200:
            models = r.json()
            self.new_encodings.emit(models)
            return models
        else:
            self.logger.error('HTTP {} error occurred while getting encodings of user n°{}.'.format(r.status_code, user_id))
            self.logger.error(r.content)

    def get_notifications(self):
        """
        Get notifications

        -------
        dict
            This function send a dictionary containing the notifications
        """
        r = requests.get(self.url + '/api/notifications', headers=self.headers)
        # Receive response
        if r.status_code == 200:
            notifs = r.json()
            self.new_notifications.emit(notifs)
            return notifs
        else:
            self.logger.error(
                'HTTP {} error occurred while getting notifications.'.format(r.status_code))
            self.logger.error(r.content)

    def get_users(self):
        """
        Get users from the memory of the Surirobot

        Returns
        -------
        list
            This function send list of all users
        """
        r = requests.get(self.url + '/api/memory/users/', headers=self.headers)
        # Receive response
        if r.status_code == 200:
            users = r.json()
            self.users_list.emit(users)
            return users
        else:
            self.logger.error('HTTP {} error occurred while getting all users.'.format(r.status_code))
            self.logger.error(r.content)

    def get_user(self, user_id):
        """
        Get user from the memory of the Surirobot

        Returns
        -------
        list
            This function send list of all users
        """
        r = requests.get(self.url + '/api/memory/users/{}/'.format(user_id), headers=self.headers)
        # Receive response
        if r.status_code == 200:
            user = r.json()
            return user
        else:
            self.logger.error('HTTP {} error occurred while getting user n°{}.'.format(r.status_code, user_id))
            self.logger.error(r.content)

    def get_last_sensor(self, sensor_type):
        """
        Get last sensor data of specified type from the memory of the Surirobot

        Parameters
        ----------
        sensor_type
            str
        Returns
        -------
        list
            This function send list of all users

        """
        r = requests.get(self.url + '/api/memory/sensors/last/' + sensor_type + '/', headers=self.headers)
        # Receive response
        if r.status_code == 200:
            sensor = r.json()
            self.new_sensor_last.emit(sensor)
            return sensor
        else:
            self.logger.error('HTTP {} error occurred while getting last sensor.'.format(r.status_code))
            self.logger.error(r.content)

    def get_sensors(self, sensor_type, t_from, t_to):
        """
        Get sensors data of type specified between the 2 time intervals

        Parameters
        ----------
        sensor_type
            str
        t_to
            int
        t_from
            int
        Returns
        -------
        list
            This function send list of all users

        """
        r = requests.get('{}/api/memory/sensors/{}/{}/{}/'.format(self.url, t_from, t_to, sensor_type), headers=self.headers)
        # Receive response
        if r.status_code == 200:
            sensors = r.json()
            self.new_sensors.emit(sensors)
            return sensors
        else:
            self.logger.error('HTTP {} error occurred while getting last sensor.'.format(r.status_code))
            self.logger.error(r.content)

    def add_user(self, firstname, lastname, email=None):
        """
        Add a user on the memory of the Surirobot

        Parameters
        ----------
        firstname : str
            firstname of user
        lastname : str
            lastname of user
        email : str
            email of user

        Returns
        -------
        dict
            This function send a user dictionary and signal
        """
        # Send request
        data = {"firstname": firstname, "lastname": lastname}

        if email:
            data['email'] = email
        r = requests.post(self.url + '/api/memory/users/', json=data, headers=self.headers)

        # Receive response
        if r.status_code == 201 or r.status_code == 200:
            user = r.json()
            self.new_user.emit(user)
            return user
        else:
            self.logger.error('HTTP {} error occurred while adding user.'.format(r.status_code))
            self.logger.error(r.content)

    def add_encoding(self, face, user_id):
        """
        Add an encoding on the memory of the Surirobot

        Parameters
        ----------
        face : list
            encodings
        user_id : int
            id of user
        Returns
        -------
        dict
            This function send a user dictionary and signal
        """
        # Send request
        data = {"value": " ".join(map(str, face)), "user": user_id}
        r = requests.post(self.url + '/api/memory/encodings/', json=data, headers=self.headers)

        # Receive response
        if r.status_code == 201 or r.status_code==200:
            model = r.json()
            self.new_encoding.emit(model)
            return model
        else:
            self.logger.error('HTTP {} error occurred while adding encoding.'.format(r.status_code))
            self.logger.error(r.content)
