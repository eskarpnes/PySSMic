import pickle
import queue
from .consumer import Consumer
from .producer import Producer
import logging
from util.message_utils import Action


class Manager:

    def __init__(self, simulator, algo="SLSQP"):
        self.logger = logging.getLogger("src.Manager")
        self.simulator = simulator
        self.consumers = []
        self.producers = {}
        self.producer_rankings = self.load_producer_scores()
        self.algo = algo
        # The simulated neighbourhood. Calling neighbourhood.now() will get the current time in seconds since
        # simulator start
        self.clock = simulator.neighbourhood

    def send_new_prediction(self, prediction, producer):
        """Send out a new weather prediction"""
        producer.tell({
            'sender': '',
            'action': Action.prediction,
            'prediction': prediction
        })

    def broadcast_new_producer(self, producer):
        """Broadcasts new producers so existing consumers can use them"""
        for consumer in self.consumers:
            consumer.tell({
                'sender': '',
                'action': Action.broadcast,
                'producer': producer
            })

    def register_producer(self, producer, id):
        """Register a new producer. Every consumer should be notified about this producer"""
        self.producers[id] = producer
        if id not in self.producer_rankings.keys():
            self.producer_rankings[id] = 10
        self.broadcast_new_producer(producer)

    def register_consumer(self, consumer):
        self.consumers.append(consumer)
        consumer._actor.request_producer()

    def register_contract(self, contract):
        self.simulator.register_contract(contract)

    def terminate_producers(self):
        """Stop all producer threads."""
        self.logger.info("Killing producers ...")
        for producer in self.producers.values():
            producer.stop()
        self.producers = {}

    def terminate_consumers(self):
        """Stop all consumer threads."""
        self.logger.info("Killing consumers ...")
        for consumer in self.consumers:
            consumer.stop()
            self.consumers = []

    # Input API
    def new_job(self, job):
        """A job contains an earliest start time, latest start time and load profile"""
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
        """Notifies the producer about the new power prediction."""
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
        pathname = self.simulator.DATA_DIR + "producer_scores"
        with open(pathname + '.pkl', 'wb') as f:
            pickle.dump(self.producer_rankings, f, pickle.HIGHEST_PROTOCOL)

    def load_producer_scores(self):
        pathname = self.simulator.DATA_DIR + "producer_scores"
        try:
            with open(pathname + '.pkl', 'rb') as f:
                self.logger.info("Loading producer scores from file.")
                producer_rankings = pickle.load(f)
        except FileNotFoundError:
            self.logger.info("No score file found. Making a fresh producer scoreboard")
            producer_rankings = {}
        return producer_rankings

    def reward_producer(self, id):
        self.producer_rankings[id] -= 1

    def punish_producer(self, id):
        self.producer_rankings[id] += 1
