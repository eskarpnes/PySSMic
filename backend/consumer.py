from pykka import ThreadingActor, Timeout
import logging
from util.message_utils import Action
import util.conf_logger


class Consumer(ThreadingActor):

    def __init__(self, producers, job, manager):
        super(Consumer, self).__init__()
        self.producers = producers
        self.job = job
        self.id = job.id
        self.logger = logging.getLogger("src.Consumer")
        self.manager = manager
        self.clock = manager.clock
        self.logger.info("New consumer made with id: " + str(self.id))

    # Send a message to another actor in a framework agnostic way
    def send(self, message, receiver):
        # Sends a blocking message to producers
        try:
            answer = receiver.ask(message, timeout=60)
            action = answer['action']
            if action == Action.decline:
                self.logger.info('Job declined. Time = ' + str(self.clock.now))
                self.producers.pop()
                self.request_producer()
            else:
                self.logger.info('Job accepted. Time = ' + str(self.clock.now))
        except Timeout:
            self.request_producer()

    # Receive a message in a framework agnostic way
    def receive(self, message, sender):
        action = message['action']
        if action == Action.broadcast:
            self.producers.append(message['producer'])
        elif action == Action.cancel:
            # TODO Implement renegotiation when a contract is cancelled
            pass

    # Function for selecting a producer for a job
    def request_producer(self):
        # TODO Implement priority queue
        if len(self.producers) <= 0:
            self.logger.info("No producer remaining. Buying power from the grid.")
            self.manager.register_contract(self.create_grid_contract(self.job))
            self.stop()
            return
        producer = self.producers[0]
        message = {
            'sender': self.actor_ref,
            'action': Action.request,
            'job': self.job
        }
        self.send(message, producer)

    # If the consumer buys power from the grid, they make a grid-contract
    def create_grid_contract(self, job):
        current_time = self.clock.now
        id = "grid" + ";" + job.id + ";" + str(current_time)
        time = job.scheduled_time
        time_of_agreement = current_time
        load_profile = job.load_profile
        job_id = job.id
        producer_id = "grid"

        return dict(id=id, time=time, time_of_agreement=time_of_agreement, load_profile=load_profile,
                    job_id=job_id, producer_id=producer_id)

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        self.receive(message, sender)
