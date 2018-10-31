from multiprocessing import Process, cpu_count, Value
from simulator import Simulator
import pickle
import os
import shutil


class ThreadedSimulator:
    def __init__(self, config):
        self.runs = config["runs"]
        self.config = config
        print("You have " + str(cpu_count()) + " cores.")
        print("This program will run " + str(self.runs / cpu_count()) + " simulations per core.")

    def start(self):
        processes = []
        if not os.path.isdir("tmp"):
            os.makedirs("tmp")
        for i in range(self.runs):
            save_name = os.path.join("tmp", "run" + str(i))
            process = Process(target=self.start_simulation, args=(save_name,))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        return self.unpickle_array()

    def start_simulation(self, name):
        sim = Simulator(self.config, name)
        sim.start()

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
        "neighbourhood": "small_test",
        "timefactor": 0.0000000000001,
        "length": 86400,
        "runs": 8
    }

    sim = ThreadedSimulator(config)
    results = sim.start()
    print(len(results[0]))
    print(len(results[1]))
