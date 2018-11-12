from enum import Enum


class Action(Enum):
    request = 'REQUEST'
    broadcast = 'BROADCAST'
    accept = 'ACCEPT'
    decline = 'DECLINE'
    prediction = 'PREDICTION'
