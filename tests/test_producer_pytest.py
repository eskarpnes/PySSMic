from backend.consumer import Consumer
from backend.job import Job
from backend.manager import Manager
from backend.producer import Producer
import pandas as pd
import numpy as np
from simulator import Simulator


def test_create_contract():
    sim = Simulator()
    manager = Manager(sim)
    producer = Producer("producer_id", manager)
    job = Job(est=0, lst=0, id="job_id", load_profile=pd.Series())
    expected = dict(id='producer_id;job_id;0', time=0, time_of_agreement=0, load_profile=pd.Series(),
                    job_id='job_id', producer_id='producer_id')
    actual = producer.create_contract(job)

    assert expected['id'] == actual['id']
    assert expected['time'] == actual['time']
    assert expected['time_of_agreement'] == actual['time_of_agreement']
    assert expected['job_id'] == actual['job_id']
    assert expected['producer_id'] == actual['producer_id']