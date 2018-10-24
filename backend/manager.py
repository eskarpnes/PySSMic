import queue
from .consumer import Consumer
from .producer import Producer
import logging
from util.message_utils import Action


class Manager:
    def __init__(self, simulator=None):
        self.consumers = []
        self.producers = {}
        self.producer_rankings = {}
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
        self.producer_rankings[id] = 10
        self.broadcast_new_producer(producer)

    # Register a new consumer
    def register_consumer(self, consumer):
        self.consumers.append(consumer)
        consumer._actor.request_producer()

    def register_contract(self, contract):
        self.simulator.register_contract(contract)

    def terminate_producers(self):
        self.logger.info("Killing producers ...")
        for producer in self.producers.values():
            producer.stop()
        self.producers = {}

    def terminate_consumers(self):
        self.logger.info("Killing consumers ...")
        for consumer in self.consumers:
            consumer.stop()
            self.consumers = []

    # Input API
    # A job contains an earliest start time, latest start time and load profile
    # (seconds elapsed and power used)
    # TODO: Load profile should be a data set designed for the optimizer algorithm
    def new_job(self, job):
        ranked_producers = queue.PriorityQueue()
        # To settle tie-breakers in the priority queue
        # Without this the priority queue tries to compare the dictionaries if the score is the same
        counter = 0
        for key, producer in self.producers.items():
            ranked_producers.put((self.producer_rankings[key], counter, {"id": key, "producer": producer}))
            counter += 1
        consumer_ref = Consumer.start(ranked_producers, job, self)
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

    def get_production_profiles(self):
        production_profiles = {}
        for producer in self.producers.values():
            production_profiles[producer._actor.id] = producer._actor.prediction
        return production_profiles

    def save_producer_scores(self):
        pass

    def load_producer_scores(self):
        pass

    def reward_producer(self, id):
        self.producer_rankings[id] += 1

    def punish_producer(self, id):
        self.producer_rankings[id] -= 1
