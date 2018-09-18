import pykka


class Manager:
    def __init__(self):
        self.consumers = []
        self.producers = []

    # Register a new consumer.
    def register_consumer(self, consumer):
        pass

    # Register a new producer. Every consumer should be notified about this producer.
    def register_producer(self, producer):
        pass

    # Send out a new weather prediction
    def broadcast_new_prediction(self):
        pass

    def fetch_producers(self):
        pass

    def new_job(self, load_profile, est, lst):
        pass
