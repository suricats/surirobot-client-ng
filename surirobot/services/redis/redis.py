import functools
import logging
from threading import Thread
import redis
from PyQt5.QtCore import QThread, pyqtSignal

from surirobot.core.common import ehpyqtSlot, QSuperTimer, State


class RedisService(QThread):
    LISTEN_INTERVAL = 1000
    update_state = pyqtSignal(str, int, dict)
    MODULE_NAME = 'redis'

    def __init__(self, url, port=6379):
        QThread.__init__(self)
        self.listenTasks = {}
        self.logger = logging.getLogger(type(self).__name__)
        self.redis = redis.StrictRedis(host=url, port=port)
        self.pub = self.redis.pubsub()

    def __del__(self):
        for key, value in self.listenTasks.items():
            try:
                value['timer'].stop()
            except:
                pass

    def listen(self, channel):
        if not self.listenTasks.get(channel):
            p = self.redis.pubsub()
            p.subscribe(channel)
            func = functools.partial(self.listen_thread, channel)
            timer = QSuperTimer()
            timer.timeout.connect(func)
            timer.setInterval(self.LISTEN_INTERVAL)
            self.listenTasks[channel] = {'pub': p, 'timer': timer}
            timer.start()

    def mute(self, channel):
        if self.listenTasks.get(channel):
            self.listenTasks[channel]['timer'].stop()
            del self.listenTasks[channel]

    def listen_process(self, channel):
        p: redis.client.PubSub = self.listenTasks[channel]['pub']
        message = p.get_message(timeout=self.LISTEN_INTERVAL / 2000, ignore_subscribe_messages=True)
        if message:
            command = message['data']
            if type(command) == bytes:
                command = command.decode('utf-8')
            print(command)
            self.update_state.emit(self.MODULE_NAME, State.REDIS_NEW, {"data" : command})

    @ehpyqtSlot()
    def listen_thread(self, channel):
        Thread(target=self.listen_process, args=[channel]).start()
