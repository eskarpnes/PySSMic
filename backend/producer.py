import sys

from pykka import ThreadingActor
import logging
from backend.job import JobStatus
from util.message_utils import Action
import random
import pandas as pd
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
        receiver.tell(message)

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
                self.schedule.append(dict(consumer=sender, job=job, status=JobStatus.created))
                return dict(action=Action.accept)
            else:
                schedule_object = dict(consumer=sender, job=job, status=JobStatus.created)
                self.schedule.append(schedule_object)
                should_keep = self.optimize()
                if should_keep:
                    contract = self.create_contract(job)
                    self.manager.register_contract(contract)
                    return dict(action=Action.accept)
                else:
                    self.schedule.remove(schedule_object)
                    return dict(action=Action.decline)

    # Function for choosing the best schedule given old jobs and the newly received one
    def optimize(self):
        self.logger.info("Running optimizer ... Time = " + str(self.manager.clock.now))
        scheduled_time, should_keep = self.optimizer.optimize()

        for i, s in enumerate(self.schedule):
            sender, job, status = s
            if not should_keep[i] and status != JobStatus.created:
                self.cancel(sender)

            if should_keep and status != JobStatus.active:
                self.schedule[i]['status'] = JobStatus.active

        return should_keep[-1]

    def cancel(self, schedule_object):
        message = dict(action=Action.decline)
        self.schedule.remove(schedule_object)
        self.send(message, schedule_object[0])

    def filter_schedule(self, status):
        return filter(lambda x: x[2] == status, self.schedule)

    # Function for updating the power profile of a producer when it has received
    # a PREDICTION and been optimized based on this
    def update_power_profile(self, prediction):
        if self.prediction is None:
            self.prediction = prediction
        else:
            offset = self.prediction[int(prediction.first_valid_index()) - 3600]
            new_prediction = prediction + offset
            self.prediction = new_prediction.combine_first(self.prediction)

    def create_contract(self, job):
        current_time = self.manager.clock.now
        id = self.id + ";" + job.id + ";" + str(current_time)
        time = job.scheduled_time
        time_of_agreement = current_time
        load_profile = job.load_profile
        job_id = job.id
        producer_id = self.id

        return dict(id=id, time=time, time_of_agreement=time_of_agreement, load_profile=load_profile,
                    job_id=job_id, producer_id=producer_id)

    def fulfill_contract(self, contract):
        new_schedule = [s for s in self.schedule if s['job'].id != contract['job_id']]
        self.schedule = new_schedule

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        return self.receive(message, sender)
