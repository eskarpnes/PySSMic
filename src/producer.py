from pykka import ThreadingActor

from src import optimizer


class Producer(ThreadingActor):
    def __init__(self, power_rating):
        super(Producer, self).__init__()
        self.power_rating = power_rating
        self.optimizer = optimizer.Optimizer()
        self.consumers = []

    # Send a message to another actor in a framework agnostic way
    def send(self, message, receiver):
        pass
        #1: ACCEPT contract
        #2: CANCEL contract
        #2: DECLINE contract

    # Receive a message in a framework agnostic way
    def receive(self, message, sender):
        action = message['action']

        if action == 'PREDICTION':
            self.update_power_profile()
            self.optimize()
        elif action == 'REQUEST':
            self.optimize()
        elif action == 'CANCEL':
            pass

    # Function for choosing the best schedule given old jobs and the newly received one
    def optimize(self):
        self.optimizer.optimize()

    # Function for updating the power profile of a producer when it has received
    # a PREDICTION and been optimized based on this
    def update_power_profile(self):
        pass

    # FRAMEWORK SPECIFIC CODE
    # Every message should have a sender field with the reference to the sender
    def on_receive(self, message):
        sender = message['sender']
        self.receive(message, sender)
