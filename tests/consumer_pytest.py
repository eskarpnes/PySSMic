from src.consumer import Consumer
from src.job import Job, JobStatus
from src.load_profile import LoadProfile
from src.producer import Producer


def test_request_producer():
    producer = Producer.start(1)
    job = Job(est=-1, lst=1, load_profile=LoadProfile([0.0, 3600.0], [0.0, 1.0]))
    consumer = Consumer.start([producer], job)

    consumer._actor.request_producer()

    assert (consumer, job, JobStatus.created) in producer._actor.schedule
