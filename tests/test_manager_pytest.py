from src.backend.manager import Manager
from src.backend.producer import Producer


def test_register_producer():
    # Make a manager with no neighbourhood (not needed for testing)
    manager = Manager()
    producer = Producer(1000)
    manager.register_producer(producer)
    assert producer in manager.producers
