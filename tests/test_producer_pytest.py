from backend.consumer import Consumer
from backend.job import Job, JobStatus
from backend.manager import Manager
from backend.producer import Producer
import pandas as pd
import numpy as np
from simulator import Simulator


def test_create_contract():
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    producer = Producer("producer_id", manager)
    job = Job(est=0, lst=0, id="job_id", load_profile=pd.Series())
    expected = dict(id='producer_id;job_id;0', time=0, time_of_agreement=0, load_profile=pd.Series(),
                    job_id='job_id', producer_id='producer_id')
    actual = producer.create_contract(job)

    assert expected['id'] == actual['id']
    assert expected['time'] == actual['time']
    assert expected['time_of_agreement'] == actual['time_of_agreement']
    assert expected['job_id'] == actual['job_id']
    assert expected['producer_id'] == actual['producer_id']


def test_cancel():
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    producer = Producer("producer_id", manager)
    job = Job(est=0, lst=0, id="job_id", load_profile=pd.Series())
    consumer = Consumer.start(producers=[producer], job=job, manager=manager)
    schedule_object = dict(consumer=consumer, job=job, status=JobStatus.created)

    producer.schedule.append(schedule_object)
    assert (schedule_object in producer.schedule)
    producer.cancel(schedule_object)
    assert producer.schedule == []
    consumer.stop()


def test_update_power_profile():
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    producer = Producer("producer_id", manager)

    p1 = pd.Series(index=[0, 3600, 7200, 10800], data=[0.0, 1.0, 2.0, 3.0])
    p2 = pd.Series(index=[7200, 10800, 14400, 18000], data=[5.0, 6.0, 7.0, 8.0])

    expected1 = p1
    expected2 = pd.Series(index=[0, 3600, 7200, 10800, 14400, 18000], data=[0.0, 1.0, 6.0, 7.0, 8.0, 9.0])

    assert producer.prediction is None
    producer.update_power_profile(p1)
    assert producer.prediction.equals(expected1)
    producer.update_power_profile(p2)
    assert producer.prediction.equals(expected2)


def test_fulfill_contract():
    sim = Simulator(dict(), None)
    manager = Manager(sim)
    producer = Producer("producer_id", manager)

    job = Job(est=0, lst=0, id="job_id", load_profile=pd.Series())
    consumer = Consumer.start(producers=[producer], job=job, manager=manager)
    schedule_object = dict(consumer=consumer, job=job, status=JobStatus.created)
    producer.schedule.append(schedule_object)
    contract = producer.create_contract(job)
    consumer.stop()

    assert producer.schedule == [schedule_object]
    producer.fulfill_contract(contract)
    assert producer.schedule == []
