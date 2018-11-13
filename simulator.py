import logging
from backend.manager import Manager
import simpy.rt
import simpy
from util.input_utils import *
from definitions import ROOT_DIR
import os.path
import pickle


class Simulator:
    def __init__(self, config, save_name):
        self.logger = logging.getLogger("src.Simulator")

        self.save_name = save_name

        # Default 1000 simulated seconds per second. 1 day = 86 seconds to run.
        factor = config["timefactor"] if "timefactor" in config else 0.001

        self.neighbourhood = simpy.rt.RealtimeEnvironment(factor=factor, strict=False)

        # Default to one day
        self.end_time = config["length"] if "length" in config else 86400

        # A dictionary over every timeout event containing a contract and the id to fetch that event
        self.active_contracts = {}

        # A list of completed contracts
        self.fulfilled_contracts = []

        # A dict of production profiles
        self.production_profiles = {}

        # Name of the configuration to be ran. Defaults to "test"
        config_name = config["neighbourhood"] if "neighbourhood" in config else "test"

        self.DATA_DIR = os.path.join(ROOT_DIR, "input", config_name)

        # The manager that is simulated. Every new load and prediction should be sent to it.
        algo = config["algo"] if "algo" in config else "L_BFGS_B"
        self.manager = Manager(self, algo)

        # Loads in events and normalizes them
        events, predictions = self.load_files_from_csv(config_name)
        events, predictions = normalize_times(events, predictions)

        # Schedule everything
        for event in events:
            schedule = self.schedule_load(event["timestamp"], event["job"])
            simpy.events.Process(self.neighbourhood, schedule)

        for prediction in predictions:
            schedule = self.schedule_prediction(prediction["timestamp"], prediction)
            simpy.events.Process(self.neighbourhood, schedule)

        simpy.events.Process(self.neighbourhood, self.end_simulation())

    # Functions that schedule the events. Simpy-specific
    def schedule_load(self, delay, job):
        event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=job)
        yield event
        self.new_load(job)

    def schedule_prediction(self, delay, prediction):
        event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=prediction)
        yield event
        self.new_prediction(prediction)

    def stop(self):
        self.manager.save_producer_scores()
        self.manager.terminate_producers()
        self.manager.terminate_consumers()

    # Starts a new consumer event
    # Will call corresponding function in manager
    def new_load(self, job):
        self.logger.info("A new load happened! Time=" + str(self.neighbourhood.now))
        self.manager.new_job(job)

    # Sends out a new weather prediction (every 6 hours)
    # Will call corresponding function in manager
    def new_prediction(self, prediction):
        self.logger.info("A new prediction happened! Time=" + str(self.neighbourhood.now))
        self.manager.new_prediction(prediction)

    # Register a contract between a consumer and producer
    # It is added as a Simpy event with a timeout until it should start
    def register_contract(self, contract):
        self.neighbourhood.process(self.register_new_contract(contract))

    def register_new_contract(self, contract):
        self.logger.info("Registering contract. Time = " + str(self.neighbourhood.now))
        id = contract["id"]
        contract_time = contract["time"]
        delay = contract_time - self.neighbourhood.now
        try:
            event = self.neighbourhood.timeout(delay)
            self.active_contracts[id] = event
            yield event
            self.fulfill_contract(contract)
        except simpy.Interrupt as i:
            self.logger.info("Contract with id " + str(id) + " was interrupted.")

    # Cancel a contract between a consumer and producer
    # Makes sure that invalid contracts won't be executed
    def cancel_contract(self, contract):
        id = contract["id"]
        event = self.active_contracts[id]
        event.interrupt()

    # Call when a contract is fulfilled.
    def fulfill_contract(self, contract):
        self.logger.info(
            "Contract fulfilled. Contract id: " + str(contract["id"]) + " Time: " + str(self.neighbourhood.now))
        if contract['producer_id'] != 'grid':
            producer = self.manager.producers[contract['producer_id']]
            producer._actor.fulfill_contract(contract)
        self.fulfilled_contracts.append(contract)

    # Loading functions
    def load_files_from_csv(self, name):
        events = get_events_from_csv(name)
        predictions = get_predictions_from_csv(name)
        return events, predictions

    # Starts the simulation
    def start(self):
        self.logger.info("Starting simulation")
        self.neighbourhood.run(until=self.end_time)

    def get_output(self):
        self.update_production_profiles()
        return self.fulfilled_contracts, self.production_profiles

    def update_production_profiles(self):
        self.production_profiles = self.manager.get_production_profiles()

    def end_simulation(self):
        event = simpy.events.Timeout(self.neighbourhood, delay=self.end_time - 1)
        yield event
        self.logger.info("Finishing run")
        self.save_output()

    def save_output(self):
        contracts, profiles = self.get_output()
        with open(self.save_name + '.pkl', 'wb') as f:
            pickle.dump((contracts, profiles), f)
        self.stop()


if __name__ == "__main__":
    import time


    # Hardcoded example

    def callback(contracts, profiles):
        print(contracts)
        print(profiles)


    config = {
        "neighbourhood": "test",
        "timefactor": 0.0000001,
        "length": 86400,
        "algo": "SLSQP"
    }

    sim = Simulator(config, callback)
    sim.start()
    time.sleep(config["length"] * config["timefactor"])
    print(sim.manager.producer_rankings)
    sim.stop()
