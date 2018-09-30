from enum import Enum

from src.job import Job
from src.load_profile import LoadProfile


class Action(Enum):
    request = 'REQUEST'
    broadcast = 'BROADCAST'
    cancel = 'CANCEL'
    accept = 'ACCEPT'
    decline = 'DECLINE'
    prediction = 'PREDICTION'


def job_from_message(message):
    return Job(est=message['est'], lst=message['lst'],
               load_profile=message['load_profile'])
