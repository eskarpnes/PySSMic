from pykka import ThreadingActor
import optimizer


class Producer(ThreadingActor):
    def __init__(self, power_rating):
        super(Producer, self).__init__()
        self.power_rating = power_rating
        self.optimizer = optimizer.Optimizer()
        self.consumers = []

    # Send a message to another actor in a framework agnostic way
    def send(self, message, receiver):
        pass

    # Receive a message in a framework agnostic way
    def receive(self, message, sender):
        pass

    # Function for choosing the best schedule given old jobs and the newly received one
    def optimize(self, job):
        pass

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        self.receive(message, sender)
