from pykka import ThreadingActor, Timeout


class Consumer(ThreadingActor):
    def __init__(self, producers, job):
        super(Consumer, self).__init__()
        self.producers = producers
        self.job = job

    # Send a message to another actor in a framework agnostic way
    def send(self, message, receiver):
        # Sends a blocking message to producers
        try:
            answer = receiver.ask(message, timeout=60)
            action = answer['action']
            if action == 'DECLINE':
                self.request_producer()
            else:
                self.register_contract()
        except Timeout:
            self.request_producer()

    # Receive a message in a framework agnostic way
    def receive(self, message, sender):
        action = message['action']
        if action == 'BROADCAST':
            self.producers.append(message['producer'])
        elif action == 'CANCEL':
            # TODO Implement renegotiation when a contract is cancelled
            pass

    # Function for selecting a producer for a job
    def request_producer(self):
        # TODO Implement priority queue
        producer = self.producers.pop()
        # TODO Check if pykka can send own actor reference as 'sender' field
        message = {
            'sender': '',
            'action': 'REQUEST',
            'job': self.job
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
