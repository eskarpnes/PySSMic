from src.backend.job import Job
import pandas as pd
import pytest


def test_to_message():
    load_profile = pd.Series(index=[0.0, 3600.0], data=[0.0, 1.0])
    job = Job(0, 1, load_profile)

    expected = dict(est=0, lst=1, load_profile=load_profile)
    actual = job.to_message()

    assert expected == actual


def test_power():
    job1 = Job(1, 2, pd.Series(index=[0.0, 1.0, 3.0, 4.0], data=[0.0, 10.0, 30.0, 40.0]))
    job2 = Job(0, 1, pd.Series(index=[0.0, 3600.0], data=[0.0, 1.0]))

    expected1 = 0.0
    expected2 = 0.0
    expected3 = pytest.approx(15.0, 0.1)
    expected4 = pytest.approx(23.0, 0.1)
    expected5 = 40.0
    expected6 = 40.0
    expected7 = pytest.approx(0.5, 0.1)

    actual1 = job1.power(-1)
    actual2 = job1.power(0)
    actual3 = job1.power(1.5)
    actual4 = job1.power(2.3)
    actual5 = job1.power(4.0)
    actual6 = job1.power(100000)
    actual7 = job2.power(1800)

    assert expected1 == actual1
    assert expected2 == actual2
    assert expected3 == actual3
    assert expected4 == actual4
    assert expected5 == actual5
    assert expected6 == actual6
    assert expected7 == actual7
