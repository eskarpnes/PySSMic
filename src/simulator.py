import logging
from src.backend.manager import Manager
import simpy.rt
import simpy
from util.input_utils import *


class Simulator:
    def __init__(self, loads, predictions):
        self.logger = logging.getLogger("src.Simulator")

        # should be initiated based on some sort of configuration scheme
        self.neighbourhood = simpy.rt.RealtimeEnvironment(factor=0.0001, strict=False)

        # Start time for the simulation. A new day starts at 0, and it counts from there in (simulated) seconds.
        self.start_time = 0

        # One day (24*60*60)
        self.end_time = 86400

        # The manager that is simulated. Every new load and prediction should be sent to it.
        self.manager = Manager(self.neighbourhood)

        # A dictionary over every timeout event containing a contract and the id to fetch that event
        self.active_contracts = {}



        # Schedule everything
        for load in loads:
            schedule = self.schedule_load(load["timestamp"], load["job"])
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
    def new_prediction(self, predictiton):
        print("A new prediction happened! Time=" + str(self.neighbourhood.now))

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
    def load_jobs_from_csv(self, filename):
        loads = get_events_from_csv(filename)
        # Schedule everything
        for load in loads:
            schedule = self.schedule_load(load["timestamp"], load["job"])
            simpy.events.Process(self.neighbourhood, schedule)

    # TODO Implement csv loading
    def load_predictions_from_csv(self):
        pass



    # Starts the simulation
    def start(self):
        print("####################")
        print("Starting simulation")
        print("####################\n")
        self.neighbourhood.run(until=self.end_time)


if __name__ == "__main__":
    # Hardcoded examples
    loads = []

    predictions = [
        {
            "timestamp": 0,
            "prediction": None
        },
        {
            "timestamp": 21600,
            "prediction": None
        },
        {
            "timestamp": 43600,
            "prediction": None
        },
        {
            "timestamp": 64800,
            "prediction": None
        }

    ]

    sim = Simulator(loads, predictions)
    # sim.start()
