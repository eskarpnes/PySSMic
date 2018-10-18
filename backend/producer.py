import sys

from pykka import ThreadingActor
import logging
from backend.job import JobStatus
from util.message_utils import Action
import util.conf_logger
import random
import pandas as pd
from util import message_utils
from backend.optimizer import Optimizer
import time


class Producer(ThreadingActor):
    def __init__(self, id, manager):
        super(Producer, self).__init__()
        self.id = id
        self.optimizer = Optimizer(self)
        self.schedule = []
        self.prediction = None
        self.logger = logging.getLogger("src.Producer")
        self.manager = manager
        self.logger.info("New producer with made with id: " + str(self.id))

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
            self.update_power_profile(message["prediction"])
            # self.optimize()

        elif action == Action.request:
            job = message['job']
            # always accept in test
            if 'pytest' in sys.modules:
                self.schedule.append((sender, job, JobStatus.created))
                return dict(action=Action.accept)
            elif random.random() > 0.5:
                self.schedule.append((sender, job, JobStatus.created))
                # self.optimize()
                self.schedule.pop()
                return dict(action=Action.accept)
            else:
                return dict(action=Action.decline)

        elif action == Action.cancel:
            pass

    # Function for choosing the best schedule given old jobs and the newly received one
    def optimize(self):
        self.logger.info("Running optimizer ... Time = " + str(self.manager.clock.now))
        result = self.optimizer.optimize(self.schedule)

        for i, s in enumerate(self.schedule):
            sender, job, status = s

            if len(self.schedule) > 1:
                accepted = result.x[i] > 0
            else:
                accepted = result.x > 0

            if accepted and status == JobStatus.created:
                contract = self.create_contract(sender, job)
                self.manager.register_contract(contract)
            elif not accepted:
                self.cancel(sender)

        # Notify cancelled consumers
        [self.cancel(s[0]) for s in self.filter_schedule(JobStatus.cancelled)]

    def cancel(self, consumer):
        message = dict(action=Action.cancel)
        self.send(message, consumer)

    def filter_schedule(self, status):
        return filter(lambda x: x[2] == status, self.schedule)

    # Function for updating the power profile of a producer when it has received
    # a PREDICTION and been optimized based on this
    def update_power_profile(self, prediction):
        if self.prediction is None:
            self.prediction = prediction
        else:
            offset = self.prediction[int(prediction.first_valid_index())-3600]
            new_prediction = prediction+offset
            self.prediction = new_prediction.combine_first(self.prediction)

    def create_contract(self, consumer, job):
        id = random.randint  # TODO: create cool id
        time = job.scheduled_time
        time_of_agreement = int(round(time.time() * 1000))
        load_profile = job.load_profile
        consumer_id = consumer.__hash__()
        producer_id = self.__hash__()

        return dict(id=id, time=time, time_of_agreement=time_of_agreement, load_profile=load_profile,
                    consumer_id=consumer_id, producer_id=producer_id)

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        return self.receive(message, sender)
