
import logging
from collections import defaultdict
from itertools import chain
import numpy as np
import pandas as pd
from random import randint

from scipy import optimize, math

from util import load_profile_utils


class Optimizer:
    def __init__(self, producer):
        self.producer = producer
        self.logger = logging.getLogger("src.Optimizer")

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self, schedule):
        objective = [0 for x in self.producer.schedule]
        # bounds = list(map(lambda x: (x[1].est, x[1].lst), schedule))
        return optimize.minimize(self.to_minimize, objective, tol=1.0, method="powell")

    def to_minimize(self, schedule):
        indices = list(set(chain.from_iterable(
            map(lambda x: self.producer.schedule[x][1].load_profile.index.values.tolist(), range(0, len(schedule))))))
        indices.sort()

        consumed = 0
        produced = 0
        penalty = 0
        for t in indices:
            consumed_t = 0
            for i, j in enumerate(schedule):
                if j > 0.0:
                    consumed_t += load_profile_utils.power(self.producer.schedule[i][1].load_profile, t)
            produced_t = load_profile_utils.power(self.producer.prediction, t)

            produced += produced_t
            consumed += consumed_t
            if produced_t - consumed_t < 0:
                penalty += 1

        score = math.fabs(produced - consumed) + penalty * 0
        return score
