import time

from backend.manager import Manager
from backend.optimizer import Optimizer

import pandas as pd
from backend.job import Job, JobStatus
from backend.producer import Producer
from simulator import Simulator


def test_optimize_basinhopping():
    sim = Simulator(dict(), None)
    man = Manager(sim)
    producer = Producer("id", man)
    producer.optimizer = Optimizer(producer, options=dict(algo="basinhopping", tol=0.5, eps=0.5))
    job0 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job1 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job2 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job3 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job4 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    producer.schedule = [job0, job1, job2, job3, job4]
    producer.prediction = pd.Series(index=[0, 10], data=[0.0, 100.0])

    schedule_time, should_keep = producer.optimizer.optimize()

    assert {0, 2, 4, 6, 8} == set([int(round(x)) for x in schedule_time])


def test_optimize_fiftyfifty():
    sim = Simulator(dict(), None)
    man = Manager(sim)
    producer = Producer("id", man)
    producer.optimizer = Optimizer(producer, options=dict(algo="50/50"))
    for i in range(1000):
        job = dict(consumer=None, job=Job("id"+str(i), 0, 0, pd.Series(index=[0], data=[0.0])), status=JobStatus.active)
        producer.schedule.append(job)
        schedule_time, should_keep = producer.optimizer.optimize()
        if not should_keep[-1]:
            producer.schedule.pop()

    num_accepted = len(producer.schedule)
    assert 400 < num_accepted < 600