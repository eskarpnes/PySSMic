from src.manager import Manager
from src.producer import Producer


def test_register_producer():
    manager = Manager()
    producer = Producer(1000)
    manager.register_producer(producer)
    assert producer in manager.producers

