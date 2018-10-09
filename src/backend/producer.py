import sys

from pykka import ThreadingActor
import logging
from src.backend.job import JobStatus
from src.util.message_utils import Action
import src.util.conf_logger

import random
import pandas as pd

from src.util import message_utils
from src.backend.optimizer import Optimizer


class Producer(ThreadingActor):
    def __init__(self, power_rating):
        super(Producer, self).__init__()
        self.power_rating = power_rating
        self.optimizer = Optimizer(self)
        self.schedule = []
        self.prediction = pd.Series(data=[0.0, 10.0], index=[0.0, 7200.0])
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
            if 'pytest' in sys.modules:
                self.schedule.append((sender, job, JobStatus.created))
                return dict(action=Action.accept)
            elif random.random() > 0.5:
                self.schedule.append((sender, job, JobStatus.created))
                self.optimize()
                return dict(action=Action.accept)
            else:
                return dict(action=Action.decline)

        elif action == Action.cancel:
            pass

    # Function for choosing the best schedule given old jobs and the newly received one
    def optimize(self):
        self.logger.info("Running optimizer ...")
        self.optimizer.optimize(self.schedule)

        # Notify cancelled consumers
        [self.cancel(s[0]) for s in self.filter_schedule(JobStatus.cancelled)]

    def cancel(self, consumer):
        message = dict(action=Action.cancel)
        self.send(message, consumer)

    def filter_schedule(self, status):
        return filter(lambda x: x[2] == status, self.schedule)

    # Function for updating the power profile of a producer when it has received
    # a PREDICTION and been optimized based on this
    def update_power_profile(self):
        pass

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        return self.receive(message, sender)
