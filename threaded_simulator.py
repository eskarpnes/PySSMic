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
            process = Process(target=self.start_simulation, args=(i,))
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
    from backend.optimizer import Algorithm

    start_time = time.time()
    # Hardcoded example
    config = {
        "neighbourhood": "test",
        "timefactor": 0.0000000000001,
        "length": 86400,
        "algo": Algorithm.SLSQP.value,
        "runs": 16
    }

    sim = ThreadedSimulator(config)
    results = sim.start()
    print(len(results[0]))
    print(len(results[1]))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time: " + str(elapsed_time))
