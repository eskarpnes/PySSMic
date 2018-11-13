from backend.models.job import Job
from backend.manager import Manager
from backend.producer import Producer
from tests.mocks import MockSimulator
import pandas as pd


def test_request_job_integration():
    simulator = MockSimulator()
    manager = Manager(simulator, algo="fifty_fifty")
    Producer(id="p1", manager=manager)
    manager.new_producer("p1")
    prediction = pd.Series(index=[0, 3600, 7200], data=[0.0, 10.0, 20.0])
    manager.send_new_prediction(prediction, manager.producers["p1"])
    job = Job("j1", 0, 0, pd.Series(index=[0, 3600], data=[0.0, 5.0]))

    manager.new_job(job)

    consumer = manager.consumers[0]
    consumer._actor.request_producer()
    manager.producers["p1"].stop()

    assert manager.producer_rankings["p1"] == 9



