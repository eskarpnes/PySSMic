import sys
import os

from backend.consumer import Consumer
from simulator import Simulator, Job
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.manager import Manager
from backend.producer import Producer
from .mocks import MockClock


def test_register_producer():
    # Make a manager with no neighbourhood (not needed for testing)
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    producer = Producer("id", manager)
    manager.register_producer("id", producer)
    assert producer in manager.producers


def test_terminate_producers():
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    p1 = Producer.start("P1", manager)
    p2 = Producer.start("P2", manager)
    manager.register_producer(p1, "P1")
    manager.register_producer(p2, "P2")

    manager.terminate_producers()
    assert manager.producers == {}


def test_terminate_consumers():
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    job = Job(est=0, lst=0, id="job_id", load_profile=pd.Series())
    consumer = Consumer.start(producers=[], job=job, manager=manager)
    manager.consumers = [consumer]

    manager.terminate_consumers()
    assert manager.consumers == []
