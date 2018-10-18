import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.job import Job
import util.input_utils as utils
import pandas as pd


def test_load_profile_from_csv():
    csv1 = "0 0\n60 1.0\n120 2.0\n180 3.0"
    csv2 = "0 0\n3600 1.0"

    expected1 = pd.Series(data=[0.0, 1.0, 2.0, 3.0], index=[0.0, 60.0, 120.0, 180.0])
    expected2 = pd.Series(data=[0.0, 1.0], index=[0.0, 3600.0])

    actual1 = utils.load_profile_from_csv(csv1)
    actual2 = utils.load_profile_from_csv(csv2)

    assert expected1.equals(actual1)
    assert expected2.equals(actual2)


def test_job_from_consumer_event():
    csv1 = "1460246602;1460246602;1460246622;[57]:[222]:[3];57_back_3.csv"
    expected1 = Job("id", 1460246602, 1460246622, pd.Series(index=[0.0, 3600.0], data=[0.0, 0.286903377284]))
    actual1 = utils.job_from_consumer_event(csv1, "test")

    assert expected1 == actual1
