from src.consumer import Consumer
from src.job import Job, JobStatus
from src.producer import Producer
import pandas as pd


def test_request_producer():
    producer = Producer.start(1)
    job = Job(est=-1, lst=1, load_profile=pd.Series(index=[0.0, 3600.0], data=[0.0, 1.0]))
    consumer = Consumer.start([producer], job)

    consumer._actor.request_producer()

    assert (consumer, job, JobStatus.created) in producer._actor.schedule
