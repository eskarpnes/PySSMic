from pykka import ThreadingActor

class Consumer(ThreadingActor):

    def __init__(self, producers):
        super(Consumer, self).__init__()
        self.producers = producers

    # Send a message to another actor in a framework agnostic way
    def send(self, message):
        pass

    # Receive a message in a framework agnostic way
    def receive(self, message):
        pass

    # Function for selecting a producer for a job
    def request_producer(self, job):
        pass

    # FRAMEWORK SPECIFIC CODE
    def on_receive(self, message):
        self.receive(message)
