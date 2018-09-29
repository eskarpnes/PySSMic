import numpy as np
import logging
import src.conf_logger
#import scipy


class Optimizer:
    def __init__(self):
        self.logger = logging.getLogger("src.Optimizer")
        pass

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self, schedule):
        pass
