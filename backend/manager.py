import simpy

from .consumer import Consumer
from .producer import Producer
import logging
from util.message_utils import Action


class Manager:
    def __init__(self, simulator=None):
        self.consumers = []
        self.producers = {}
        self.logger = logging.getLogger("src.Manager")

        # The simulated neighbourhood. Calling neighbourhood.now() will get the current time in seconds since
        # simulator start
        self.simulator = simulator
        self.clock = simulator.neighbourhood

    # Send out a new weather prediction
    def send_new_prediction(self, prediction, producer):
        producer.tell({
            'sender': '',
            'action': Action.prediction,
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
    def register_producer(self, producer, id):
        self.producers[id] = producer
        self.broadcast_new_producer(producer)

    # Register a new consumer
    def register_consumer(self, consumer):
        self.consumers.append(consumer)
        consumer._actor.request_producer()

    def register_contract(self, contract):
        print("Registering contract")
        self.simulator.register_contract(contract)

    def terminate_producers(self):
        for producer in self.producers.values():
            producer.stop()
        self.producers = {}

    # Input API    
    # A job contains an earliest start time, latest start time and load profile
    # (seconds elapsed and power used)
    # TODO: Load profile should be a data set designed for the optimizer algorithm
    def new_job(self, job):
        consumer_ref = Consumer.start(list(self.producers.values()), job, self.clock)
        self.register_consumer(consumer_ref)

    # Input API
    def new_producer(self, producer_id):
        producer_ref = Producer.start(producer_id, self)
        self.register_producer(producer_ref, producer_id)

    # Input API
    def new_prediction(self, prediction_event):
        producer_id = prediction_event["id"]
        if producer_id not in self.producers.keys():
            self.new_producer(producer_id)
        producer = self.producers[producer_id]
        self.send_new_prediction(prediction_event["prediction"], producer)
