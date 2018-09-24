import logging
import src.conf_logger

class Simulator:
    def __init__(self):
        self.logger = logging.getLogger("src.Simulator")
        # should be initiated based on some sort of configuration scheme
        pass

    # Starts a new consumer event
    def new_event(self):
        pass

    # Sends out a new weather prediction (every 6 hours)
    def new_prediction(self):
        pass
