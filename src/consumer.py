from pykka import ThreadingActor, Timeout
import src.conf_logger
import logging
from src.message_utils import Action


class Consumer(ThreadingActor):
    def __init__(self, producers, job):
        super(Consumer, self).__init__()
        self.producers = producers
        self.job = job
        self.logger = logging.getLogger("src.Consumer")

    # Send a message to another actor in a framework agnostic way
    def send(self, message, receiver):
        # Sends a blocking message to producers
        try:
            answer = receiver.ask(message, timeout=60)
            action = answer['action']
            if action == Action.decline:
                self.request_producer()
            else:
                self.register_contract()
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
        producer = self.producers.pop()
        message = {
            'sender': self.actor_ref,
            'action': Action.request,
            'job': self.job.to_message()
        }
        self.send(message, producer)

    def register_contract(self):
        # TODO Design contract
        pass

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        self.receive(message, sender)
