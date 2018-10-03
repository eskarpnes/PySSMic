import logging
#import scipy


class Optimizer:
    def __init__(self, producer):
        self.producer = producer
        self.logger = logging.getLogger("src.Optimizer")

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self, schedule):
        pass
