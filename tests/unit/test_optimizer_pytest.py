from backend.job import Job
from backend.manager import Manager
from backend.optimizer import Optimizer

import pandas as pd
from backend.producer import Producer
from simulator import Simulator


def test_optimize_basinhopping():
    sim = Simulator(dict(), None)
    man = Manager(sim)
    producer = Producer("id", man)
    job0 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])))
    job1 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])))
    job2 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])))
    job3 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])))
    job4 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])))

    schedules = []
    for i in range(50):
        if {0, 2, 4, 6, 8} not in schedules:
            producer.optimizer = Optimizer(producer, options=dict(algo="L_BFGS_B", tol=50.0, eps=0.01))
            producer.schedule = [job0, job1, job2, job3, job4]
            producer.prediction = pd.Series(index=[0, 10], data=[0.0, 100.0])
            schedule_time, should_keep = producer.optimizer.optimize()
            schedules.append(set([int(round(x)) for x in schedule_time]))

    assert {0, 2, 4, 6, 8} in schedules


def test_optimize_fifty_fifty():
    sim = Simulator(dict(), None)
    man = Manager(sim)
    producer = Producer("id", man)
    producer.optimizer = Optimizer(producer, options=dict(algo="fifty_fifty"))
    producer.prediction = pd.Series(index=[0, 1], data=[0.0, 1.0])
    for i in range(250):
        job = dict(consumer=None, job=Job("id" + str(i), 0, 0, pd.Series(index=[0, 1], data=[0.0, 0.0])))
        producer.schedule.append(job)
        schedule_time, should_keep = producer.optimizer.optimize()
        if not should_keep[-1]:
            producer.schedule.pop()

    num_accepted = len(producer.schedule)
    assert 100 < num_accepted < 150


def test_optimize_fifty_fifty_negative():
    sim = Simulator(dict(), None)
    man = Manager(sim)
    producer = Producer("id", man)
    producer.optimizer = Optimizer(producer, options=dict(algo="fifty_fifty"))
    producer.prediction = pd.Series(index=[0, 1], data=[0.0, 0.0])
    for i in range(10):
        job = dict(consumer=None, job=Job("id" + str(i), 0, 0, pd.Series(index=[0, 1], data=[0.0, 1.0])))
        producer.schedule.append(job)
        schedule_time, should_keep = producer.optimizer.optimize()
        if not should_keep[-1]:
            producer.schedule.pop()

    num_accepted = len(producer.schedule)
    assert 0 == num_accepted
