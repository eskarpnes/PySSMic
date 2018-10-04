import logging
from src.backend.manager import Manager
import simpy.rt
import simpy
from src.util.input_utils import *


class Simulator:
    def __init__(self, config={}):
        self.logger = logging.getLogger("src.Simulator")

        # Default 1000 simulated seconds per second. 1 day = 86 seconds to run.
        factor = config["timefactor"] if "timefactor" in config else 0.001

        self.neighbourhood = simpy.rt.RealtimeEnvironment(factor=factor, strict=False)

        # Default to one day
        self.end_time = config["length"] if "length" in config else 86400

        # The manager that is simulated. Every new load and prediction should be sent to it.
        self.manager = Manager(self.neighbourhood)

        # A dictionary over every timeout event containing a contract and the id to fetch that event
        self.active_contracts = {}

        # Name of the configuration to be ran. Defaults to "test"
        config_name = config["neighbourhood"] if "neighbourhood" in config else "test"

        # Loads in events and normalizes them
        events, predictions = self.load_files_from_csv(config_name)
        events, predictions = normalize_times(events, predictions)

        # Schedule everything
        for event in events:
            schedule = self.schedule_load(event["timestamp"], event["job"])
            simpy.events.Process(self.neighbourhood, schedule)

        for prediction in predictions:
            schedule = self.schedule_prediction(prediction["timestamp"], prediction["prediction"])
            simpy.events.Process(self.neighbourhood, schedule)

    # Functions that schedule the events. Simpy-specific
    def schedule_load(self, delay, job):
        event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=job)
        yield event
        self.new_load(job)

    def schedule_prediction(self, delay, prediction):
        event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=prediction)
        yield event
        self.new_prediction(prediction)

    # Starts a new consumer event
    # Will call corresponding function in manager
    def new_load(self, job):
        print("A new load happened! Time=" + str(self.neighbourhood.now))
        print("Load: " + str(job) + "\n")
        self.manager.new_job(job)

    # Sends out a new weather prediction (every 6 hours)
    # Will call corresponding function in manager
    def new_prediction(self, prediction):
        print("A new prediction happened! Time=" + str(self.neighbourhood.now))
        self.manager.new_prediction(prediction)

    # Register a contract between a consumer and producer
    # It is added as a Simpy event with a timeout until it should start
    def register_contract(self, contract):
        print("Registering contract")
        id = contract["id"]
        contract_time = contract["timestamp"]
        delay = contract_time - self.neighbourhood.now
        try:
            event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=id)
            self.active_contracts[id] = event
            yield event
            self.fulfill_contract(contract)
        except simpy.Interrupt as i:
            print("Contract with id " + str(id) + " was interrupted.")

    # Cancel a contract between a consumer and producer
    # Makes sure that invalid contracts won't be executed
    def cancel_contract(self, contract):
        id = contract["id"]
        event = self.active_contracts[id]
        event.interrupt()

    # Call when a contract is fulfilled.
    def fulfill_contract(self, contract):
        print("Contract fulfilled. Contract details: ")
        print(contract)
        # TODO Implement fulfillment logic

    # Loading functions
    def load_files_from_csv(self, name):
        events = get_events_from_csv(name)
        predictions = get_predictions_from_csv(name)
        return events, predictions

    # Starts the simulation
    def start(self):
        print("####################")
        print("Starting simulation")
        print("####################\n")
        self.neighbourhood.run(until=self.end_time)


if __name__ == "__main__":
    # Hardcoded example
    config = {
        "neighbourhood": "test",
        "timefactor": 0.0001,
        "length": 86400
    }
    sim = Simulator(config)
    sim.start()
