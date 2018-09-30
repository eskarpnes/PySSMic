from src.job import Job
from src.load_profile import LoadProfile


def test_to_message():
    load_profile = LoadProfile([0.0, 3600.0], [0.0, 1.0])
    job = Job(0, 1, load_profile)

    expected = dict(est=0, lst=1, load_profile=load_profile)
    actual = job.to_message()

    assert expected == actual
