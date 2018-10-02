from src.job import Job
import pandas as pd


def test_to_message():
    load_profile = pd.Series(index=[0.0, 3600.0], data=[0.0, 1.0])
    job = Job(0, 1, load_profile)

    expected = dict(est=0, lst=1, load_profile=load_profile)
    actual = job.to_message()

    assert expected == actual
