from src.job import Job
from src.load_profile import LoadProfile
import src.input_utils as utils


def test_load_profile_from_csv():
    csv1 = "0 0\n60 1.0\n120 2.0\n180 3.0"
    csv2 = "0 0\n3600 1.0"

    expected1 = LoadProfile([0.0, 60.0, 120.0, 180.0], [0.0, 1.0, 2.0, 3.0])
    expected2 = LoadProfile([0.0, 3600.0], [0.0, 1.0])

    actual1 = utils.load_profile_from_csv(csv1)
    actual2 = utils.load_profile_from_csv(csv2)

    assert expected1 == actual1
    assert expected2 == actual2


def test_job_from_consumer_event():
    csv1 = "1460246602;1460246602;1460246622;[57]:[222]:[3];57_back_3.csv"
    expected1 = Job(1460246602, 1460246622, LoadProfile([0.0, 3600.0], [0.0, 0.286903377284]))
    actual1 = utils.job_from_consumer_event(csv1)

    assert expected1 == actual1
