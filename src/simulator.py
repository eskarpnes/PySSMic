import logging
import src.conf_logger
import simpy.rt
import simpy


class Simulator:
    def __init__(self, loads, predictions):
        self.logger = logging.getLogger("src.Simulator")
        # should be initiated based on some sort of configuration scheme
        self.neighbourhood = simpy.rt.RealtimeEnvironment(factor=0.0001, strict=False)
        self.startTime = 0
        # One day (24*60*60)
        self.endTime = 86400

        # Schedule everything
        for load in loads:
            schedule = self.schedule_load(load["timestamp"], load["load"])
            simpy.events.Process(self.neighbourhood, schedule)

        for prediction in predictions:
            schedule = self.schedule_prediction(prediction["timestamp"], prediction["prediction"])
            simpy.events.Process(self.neighbourhood, schedule)

    # Functions that schedule the events. Simpy-specific
    def schedule_load(self, delay, load):
        event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=load)
        yield event
        self.new_load(load)

    def schedule_prediction(self, delay, prediction):
        event = simpy.events.Timeout(self.neighbourhood, delay=delay, value=prediction)
        yield event
        self.new_prediction(prediction)

    # Starts a new consumer event
    # Will call corresponing function in manager
    def new_load(self, load):
        print("A new load happened! Time=" + str(self.neighbourhood.now))
        print("Load: " + str(load) + "\n")

    # Sends out a new weather prediction (every 6 hours)
    # Will call corresponing function in manager
    def new_prediction(self, predictiton):
        print("A new prediction happened! Time=" + str(self.neighbourhood.now))

    # Loading functions
    def load_loads_from_csv(self):
        pass

    def load_predictions_from_csv(self):
        pass

    # Starts the simulation
    def start(self):
        self.neighbourhood.run(until=self.endTime)



if __name__ == "__main__":

    # Hardcoded examples
    loads = [
        {
            "timestamp": 1000,
            "load": {
                "est": 2000,
                "lst": 4000,
                "profile": None
            }
        },
        {
            "timestamp": 4000,
            "load": {
                "est": 6000,
                "lst": 10000,
                "profile": None
            }
        },
        {
            "timestamp": 40000,
            "load": {
                "est": 46000,
                "lst": 50000,
                "profile": None
            }
        }
    ]

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
    sim.start()
