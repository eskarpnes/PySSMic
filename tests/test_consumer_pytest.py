import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.consumer import Consumer
from backend.job import Job, JobStatus
from backend.producer import Producer
import pandas as pd
from .mock_clock import MockClock

def test_request_producer():
    producer = Producer.start("id", None)
    job = Job("id", est=-1, lst=1, load_profile=pd.Series(index=[0.0, 3600.0], data=[0.0, 1.0]))
    consumer = Consumer.start([producer], job, MockClock())

    consumer._actor.request_producer()

    assert (consumer, job, JobStatus.created) in producer._actor.schedule

    producer.stop()
    consumer.stop()
