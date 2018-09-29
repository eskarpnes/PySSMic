import sys

from pykka import ThreadingActor
import logging
from src.message_utils import Action
import pykka
import src.conf_logger
import random

from src import optimizer, message_utils
from src.job import Job


class Producer(ThreadingActor):
    def __init__(self, power_rating):
        super(Producer, self).__init__()
        self.power_rating = power_rating
        self.optimizer = optimizer.Optimizer()
        self.consumers = []
        self.logger = logging.getLogger("src.Producer")

    # Send a message to another actor in a framework agnostic way
    def send(self, message, receiver):
        pass
        # 1: ACCEPT contract
        # 2: CANCEL contract
        # 2: DECLINE contract

    # Receive a message in a framework agnostic way
    def receive(self, message, sender):
        action = message['action']

        if action == Action.prediction:
            self.update_power_profile()
            self.optimize()
        elif action == Action.request:
            job = message_utils.job_from_message(message['job'])
            # always accept in test
            if random.random() > 0.5 or 'pytest' in sys.modules:
                self.consumers.append((sender, job))
                self.optimize()
                return dict(action=Action.accept)
            else:
                return dict(action=Action.decline)

        elif action == Action.cancel:
            pass

    # Function for choosing the best schedule given old jobs and the newly received one
    def optimize(self):
        self.optimizer.optimize(self.consumers)

    # Function for updating the power profile of a producer when it has received
    # a PREDICTION and been optimized based on this
    def update_power_profile(self):
        pass

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        return self.receive(message, sender)
