from backend.models.job import Job
from backend.manager import Manager
from backend.optimizer import Optimizer
import util.optimizer_utils as utils

import pandas as pd
from backend.producer import Producer
from simulator import Simulator


def test_optimize_basinhopping():
    sim = Simulator(dict(), None)
    man = Manager(sim)
    producer = Producer("id", man)
    job0 = dict(consumer=None, job=Job("id", 0, 500, pd.Series(index=[0, 60, 120], data=[0.0, 5.0, 10.0])))
    job1 = dict(consumer=None, job=Job("id", 0, 500, pd.Series(index=[0, 60, 120], data=[0.0, 5.0, 10.0])))
    job2 = dict(consumer=None, job=Job("id", 0, 500, pd.Series(index=[0, 60, 120], data=[0.0, 5.0, 10.0])))
    job3 = dict(consumer=None, job=Job("id", 0, 500, pd.Series(index=[0, 60, 120], data=[0.0, 5.0, 10.0])))
    job4 = dict(consumer=None, job=Job("id", 0, 500, pd.Series(index=[0, 60, 120], data=[0.0, 5.0, 10.0])))

    producer.optimizer = Optimizer(producer, options=dict(algo="SLSQP", pen=1.0, tol=1.0, eps=0.01))
    producer.schedule = [job0, job1, job2, job3, job4]
    producer.prediction = pd.Series(index=[0, 300, 600], data=[0.0, 25.0, 50.0])
    schedule_time, should_keep = producer.optimizer.optimize()
    schedule = set([int(utils.round_to_nearest_60(x)) for x in schedule_time])

    # Assert that we have at least one scheduled time.
    assert len(schedule) >= 1


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
