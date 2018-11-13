from pykka import ThreadingActor, Timeout
import logging
from util.message_utils import Action


class Consumer(ThreadingActor):

    def __init__(self, producers, job, manager):
        super(Consumer, self).__init__()
        self.producers = producers
        self.job = job
        self.id = job.id
        self.logger = logging.getLogger("src.Consumer")
        self.manager = manager
        self.clock = manager.clock
        self.logger.info("New consumer made with id: " + str(self.id))

    def send(self, message, receiver):
        """Send a message to another actor in a framework agnostic way"""
        
        # Sends a blocking message to producers
        receiver_id = receiver['id']
        receiver = receiver["producer"]
        try:
            answer = receiver.ask(message, timeout=60)
            action = answer['action']
            if action == Action.decline:
                self.logger.info("Job declined. Time = " + str(self.clock.now))
                self.manager.punish_producer(receiver_id)
                self.request_producer()
            else:
                self.logger.info("Job accepted. Time = " + str(self.clock.now))
                self.manager.reward_producer(receiver_id)
        except Timeout:
            self.request_producer()

    def receive(self, message):
        """Receive a message in a framework agnostic way"""
        action = message['action']
        if action == Action.broadcast:
            self.producers.append(message['producer'])

    def request_producer(self):
        """Function for selecting a producer for a job"""
        if self.producers.empty():
            self.logger.info("No producer remaining. Buying power from the grid.")
            self.manager.register_contract(self.create_grid_contract())
            self.stop()
            return
        # The producer is the third object in the tuple. The first two are for priorities.
        producer_pri = self.producers.get()
        self.logger.info("Asking producer with ranking " + str(producer_pri[0]))
        producer = producer_pri[2]
        message = {
            'sender': self.actor_ref,
            'action': Action.request,
            'job': self.job
        }
        self.send(message, producer)

    def create_grid_contract(self):
        """If the consumer buys power from the grid, they make a grid-contract."""
        current_time = self.clock.now
        id = "grid" + ";" + self.job.id + ";" + str(current_time)
        time = self.job.scheduled_time
        time_of_agreement = current_time
        load_profile = self.job.load_profile
        job_id = self.job.id
        producer_id = "grid"
        return dict(id=id, time=time, time_of_agreement=time_of_agreement, load_profile=load_profile,
                    job_id=job_id, producer_id=producer_id)

    # FRAMEWORK SPECIFIC CODE
    def on_receive(self, message):
        """Every message should have a sender field with the reference to the sender"""
        self.receive(message)
