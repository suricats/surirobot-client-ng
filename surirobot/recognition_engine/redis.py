import os
import redis
from threading import Thread

import shared as s
from .utils import id_to_name


class RedisThread(Thread):
    def __init__(self, conn, name):
        Thread.__init__(self)
        self.conn = conn
        self.name = name

    def run(self):
        channel = os.environ.get('FACERECO_REDIS_MODULE_NAME')
        self.conn.publish(channel, self.name)


class RedisAdapter:
    last_id = -1

    def __init__(self):
        redis_address = os.environ.get('SURIROBOT_REDIS_ADDRESS', '127.0.0.1')
        self.conn = redis.StrictRedis(redis_address)

    def process(self, id):
        if self.last_id != id:
            self.last_id = id
            thread = RedisThread(self.conn, str(id) + '.' + id_to_name(id))
            thread.start()
