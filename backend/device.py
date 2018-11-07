import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.consumer_event import ConsumerEvent
from backend.producer_event import ProducerEvent
import datetime


class Device():
    def __init__(self, devId, name, template, devType):
        self.id = devId
        self.name = name
        self.template = template
        self.type = devType
        self.loadProfile = None
        self.events = []
        self.weatherPredictions1 = None
        self.weatherPredictions2 = None
        self.weatherPredictions3 = None
        self.weatherPredictions4 = None

    def add_event(self, event):
        if (isinstance(event, ConsumerEvent) and self.type == "consumer") or (isinstance(event, ProducerEvent) and self.type == "producer"):
            if(event.deviceId == self.id):
                self.events.append(event)

    def __str__(self):
        return str(self.name)


class Event():
    def __init__(self, device, time, est, lst):
        self.device = device
        self.timestamp = time
        self.est = est
        self.lst = lst

    def __str__(self):

        return self.unixToString(self.timestamp) + " event for " + self.device.name + " est " + self.unixToString(self.est) + " lst " + self.unixToString(self.lst)

    def unixToString(self, time):
        return datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
