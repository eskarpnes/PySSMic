from enum import Enum

from backend.job import Job


class Action(Enum):
    request = 'REQUEST'
    broadcast = 'BROADCAST'
    cancel = 'CANCEL'
    accept = 'ACCEPT'
    decline = 'DECLINE'
    prediction = 'PREDICTION'
