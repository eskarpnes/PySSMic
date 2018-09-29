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


def load_profile_from_message(message):
    return LoadProfile(timestamps=message['timestamps'], loads=message['loads'])


def job_from_message(message):
    return Job(est=message['est'], lst=message['lst'],
               load_profile=load_profile_from_message(message['load_profile']))