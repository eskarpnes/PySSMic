from src.backend.consumer import Consumer
from src.backend.producer import Producer
import logging
from src.util.message_utils import Action


class Manager:
    def __init__(self, clock=None):
        self.consumers = []
        self.producers = []
        self.logger = logging.getLogger("src.Manager")

        # The simulated neighbourhood. Calling neighbourhood.now() will get the current time in seconds since
        # simulator start
        self.clock = clock

    # Send out a new weather prediction
    def broadcast_new_prediction(self, prediction):
        for producer in self.producers:
            producer.tell({
                'sender': '',
                'action': Action.broadcast,
                'prediction': prediction
            })

    # Broadcasts new producers so existing consumers can use them
    def broadcast_new_producer(self, producer):
        for consumer in self.consumers:
            consumer.tell({
                'sender': '',
                'action': Action.broadcast,
                'producer': producer
            })

    # Register a new producer. Every consumer should be notified about this producer
    def register_producer(self, producer):
        self.logger.debug("Registering new producer %s", producer)
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
