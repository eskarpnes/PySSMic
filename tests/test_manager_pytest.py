import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.manager import Manager
from backend.producer import Producer
from .mock_clock import MockClock

def test_register_producer():
    # Make a manager with no neighbourhood (not needed for testing)
    manager = Manager()
    producer = Producer(manager, MockClock())
    manager.register_producer("id", producer)
    assert producer in manager.producers
