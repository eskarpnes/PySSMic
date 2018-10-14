import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.manager import Manager
from backend.producer import Producer


def test_register_producer():
    # Make a manager with no neighbourhood (not needed for testing)
    manager = Manager()
    producer = Producer(1000, manager)
    manager.register_producer(producer)
    assert producer in manager.producers
