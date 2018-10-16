import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.consumerEvent import ConsumerEvent
from backend.producerEvent import ProducerEvent


class Device():
    def __init__(self, devId, name, template, devType):
        self.id = devId
        self.name = name
        self.template = template
        self.type = devType
        self.events = []
