from multiprocessing import Queue
from multiprocessing.managers import BaseManager

from constants import AvailableTargetLanguages


class QueueManager(BaseManager):
    pass


def create_queue(host, port, authkey, queue_name) -> QueueManager:
    q = Queue()
    QueueManager.register(queue_name, callable=lambda: q)
    manager = QueueManager(address=(host, port), authkey=authkey)
    manager.start()
    return manager


def connect_queue(host, port, authkey, queue_name) -> QueueManager:
    QueueManager.register(queue_name)
    manager = QueueManager(address=(host, port), authkey=authkey)
    manager.connect()
    return manager


def validate_language(value) -> str:
    if value not in AvailableTargetLanguages:
        raise Exception("Invalid value for argument `lang`. "
                        "Available languages {}".format(AvailableTargetLanguages))
    return str(value)
