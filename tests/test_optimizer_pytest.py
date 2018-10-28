import time

from backend.manager import Manager
from backend.optimizer import Optimizer

import pandas as pd
from backend.job import Job, JobStatus
from backend.producer import Producer
from simulator import Simulator


def test_optimize():
    sim = Simulator()
    man = Manager(sim)
    producer = Producer("id", man)
    job0 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job1 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job2 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job3 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    job4 = dict(consumer=None, job=Job("id", 0, 8, pd.Series(index=[0, 1], data=[0.0, 10.0])), status=JobStatus.active)
    producer.schedule = [job0, job1, job2, job3, job4]
    producer.prediction = pd.Series(index=[0, 10], data=[0.0, 100.0])

    schedule_time, should_keep = producer.optimizer.optimize(tol=0.5, eps=0.5)

    assert {0, 2, 4, 6, 8} == set([int(round(x)) for x in schedule_time])


def test_differentiate():
    o = Optimizer(None)
    series1 = pd.Series(index=[0, 3600], data=[0.0, 1.0])
    expected1 = pd.Series(index=[0, 3600], data=[0.000278, 0.000278]).round(4)
    actual1 = o.differentiate(series1).round(4)

    series2 = pd.Series(index=[0, 1, 2, 3, 4, 5], data=[0.0, 0.5, 1.0, 2.0, 2.0, 3.0])
    expected2 = pd.Series(index=[0, 1, 2, 3, 4, 5], data=[0.5, 0.5, 1.0, 0.0, 1.0, 1.0]).round(4)
    actual2 = o.differentiate(series2).round(4)

    assert all(list(expected1 == actual1))
    assert all(list(expected2 == actual2))


def test_interpolate():
    o = Optimizer(None)
    series = pd.Series(index=[2, 4, 6], data=[4.0, 8.0, 12.0])
    actual = o.interpolate(series, [0, 1, 2, 3, 4, 5, 6, 7, 8]).round(4)
    expected = pd.Series(index=[0, 1, 2, 3, 4, 5, 6, 7, 8], data=[4.0, 4.0, 4.0, 6.0, 8.0, 10.0, 12.0, 12.0, 12.0])
    assert all(list(actual.data == expected))
