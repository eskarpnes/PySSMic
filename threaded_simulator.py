from multiprocessing import Process, cpu_count, Value
from simulator import Simulator
import pickle
import os
import shutil


class ThreadedSimulator:

    def __init__(self, config, callback):
        self.runs = config["runs"]
        self.callback = callback
        self.config = config
        self.counter = Value('i', 0)
        print("You have " + str(cpu_count()) + " cores.")
        print("This program will run " + str(self.runs / cpu_count()) + " simulations per core.")

    def start(self):
        for i in range(self.runs):
            sim = Simulator(self.config, self.get_run_results)
            process = Process(target=sim.start)
            process.start()

    def get_run_results(self, contracts, profiles):
        with self.counter.get_lock():
            index = self.counter.value
            self.counter.value += 1
            if not os.path.isdir("tmp"):
                os.makedirs("tmp")
            pathname = os.path.join("tmp", "run" + str(index))
            with open(pathname + '.pkl', 'wb') as f:
                pickle.dump((contracts, profiles), f)
            self.check_if_done()

    def check_if_done(self):
        print(str(self.counter.value) + " of " + str(self.runs) + " done.")
        if self.counter.value == self.runs:
            contracts, profiles = self.unpickle_array()
            self.callback(contracts, profiles)

    def unpickle_array(self):
        contracts, profiles = [], []
        for i in range(self.runs):
            pathname = os.path.join("tmp", "run" + str(i))
            with open(pathname + '.pkl', 'rb') as f:
                result = pickle.load(f)
            contracts.append(result[0])
            profiles.append(result[1])
        shutil.rmtree("tmp")
        return contracts, profiles


if __name__ == "__main__":
    import time

    start_time = time.time()
    # Hardcoded example
    config = {
        "neighbourhood": "test",
        "timefactor": 0.0000000000001,
        "length": 86400,
        "runs": 8
    }


    def callback(contracts, profiles):
        end_time = time.time()
        print(len(contracts))
        print(len(profiles))
        print("Elapsed time: " + str(end_time - start_time) + " seconds.")


    sim = ThreadedSimulator(config, callback)
    sim.start()
