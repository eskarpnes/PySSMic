from pykka import ThreadingActor
import logging
from util.message_utils import Action
from backend.optimizer import Optimizer


class Producer(ThreadingActor):
    def __init__(self, id, manager):
        super(Producer, self).__init__()
        self.id = id
        self.schedule = []
        self.prediction = None
        self.logger = logging.getLogger("src.Producer")
        self.manager = manager
        options = dict(algo=manager.algo)
        self.optimizer = Optimizer(self, options)
        self.logger.info("New producer with made with id: " + str(self.id))

    def send(self, message, receiver):
        """Send a message to another actor in a framework agnostic way"""
        receiver.tell(message)

    def receive(self, message, sender):
        """Receive a message in a framework agnostic way"""
        action = message['action']

        if action == Action.prediction:
            self.update_power_profile(message["prediction"])

        elif action == Action.request:
            job = message['job']
            schedule_object = dict(consumer=sender, job=job)
            self.schedule.append(schedule_object)
            should_keep = self.optimize()
            if should_keep:
                contract = self.create_contract(job)
                self.manager.register_contract(contract)
                return dict(action=Action.accept)
            else:
                self.schedule.remove(schedule_object)
                return dict(action=Action.decline)

    def optimize(self):
        """Function for choosing the best schedule given old jobs and the newly received one. Currently, it can only
        drop the last job received. Returns True if the last object in self.schedule should be kept. Returns False if it
        should be rejected."""

        self.logger.info("Running optimizer ... Time = " + str(self.manager.clock.now))
        scheduled_time, should_keep = self.optimizer.optimize()

        return should_keep[-1]

    def cancel(self, schedule_object):
        """Cancel a job."""
        message = dict(action=Action.decline)
        self.schedule.remove(schedule_object)
        self.send(message, schedule_object['consumer'])

    def update_power_profile(self, prediction):
        """Function for updating the power profile of a producer when it has received a prediction."""
        if self.prediction is None:
            self.prediction = prediction
        else:
            offset = self.prediction[int(prediction.first_valid_index()) - 3600]
            new_prediction = prediction + offset
            self.prediction = new_prediction.combine_first(self.prediction)

    def create_contract(self, job):
        """Create a contract between producer and the consumer requesting the job."""
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
        """Remove a fulfilled job from the list of jobs."""
        new_schedule = [s for s in self.schedule if s['job'].id != contract['job_id']]
        self.schedule = new_schedule

    # FRAMEWORK SPECIFIC CODE
    def on_receive(self, message):
        """Every message should have a sender field with the reference to the sender"""
        sender = message['sender']
        return self.receive(message, sender)
