from consumer import Consumer

from src.producer import Producer


class Manager:
    def __init__(self):
        self.consumers = []
        self.producers = []

    # Send out a new weather prediction
    def broadcast_new_prediction(self, prediction):
        for producer in self.producers:
            producer.tell({
                'sender': '',
                'action': 'BROADCAST',
                'prediction': prediction
            })

    # Broadcasts new producers so existing consumers can use them
    def broadcast_new_producer(self, producer):
        for consumer in self.consumers:
            consumer.tell({
                'sender': '',
                'action': 'BROADCAST',
                'producer': producer
            })

    # Register a new producer. Every consumer should be notified about this producer
    def register_producer(self, producer):
        self.producers.append(producer)
        self.broadcast_new_producer(producer)

    # Register a new consumer
    def register_consumer(self, consumer):
        self.consumers.append(consumer)

    # Input API    
    # A job contains an earliest start time, latest start time and load profile
    # (seconds elapsed and power used)
    # TODO: Load profile should be a data set designed for the optimizer algorithm
    def new_job(self, load_profile, est, lst):
        job = {
            'est': est,
            'lst': lst,
            'load': load_profile
        }
        consumer_ref = Consumer.start(self.producers, job)
        self.register_consumer(consumer_ref)

    # Input API
    # Power rating is the maximum power the PV panels can output given perfect conditions
    # Given in watts
    # Weather predictions will give a float that says how many percent of the maximum the
    # PV panels will produce
    def new_producer(self, power_rating):
        producer_ref = Producer.start(power_rating)
        self.broadcast_new_producer(producer_ref)

    # Input API
    def new_prediction(self, prediction):
        self.broadcast_new_prediction(prediction)
