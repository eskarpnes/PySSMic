import pandas as pd

from src.backend.job import Job, JobStatus
from src.backend.producer import Producer


def test_optimize():
    producer = Producer(1.0)
    job1 = (None, Job(0, 0, pd.Series(index=[0, 3], data=[40, 40])), JobStatus.active)
    job2 = (None, Job(0, 0, pd.Series(index=[2, 4], data=[30, 30])), JobStatus.active)
    job3 = (None, Job(0, 0, pd.Series(index=[5, 6], data=[10, 10])), JobStatus.active)
    job4 = (None, Job(0, 0, pd.Series(index=[5, 6], data=[40, 40])), JobStatus.active)
    job5 = (None, Job(0, 0, pd.Series(index=[7, 10], data=[50, 50])), JobStatus.active)
    job6 = (None, Job(0, 0, pd.Series(index=[7, 10], data=[40, 40])), JobStatus.active)
    producer.schedule = [job1, job2, job3, job4, job5, job6]
    producer.prediction = pd.Series(index=[0, 10], data=[50, 50])

    result = producer.optimizer.optimize(producer.schedule)
    assert result.x[0] > 0
    assert result.x[1] > 0
    assert result.x[2] > 0
    assert result.x[3] > 0
    assert result.x[4] > 0
    assert result.x[5] < 0
