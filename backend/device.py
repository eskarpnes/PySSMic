import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.consumer_event import ConsumerEvent
from backend.producer_event import ProducerEvent


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
