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
        objective = [randint(x[1].est, x[1].lst) for x in self.producer.schedule]
        bounds = list(map(lambda x: (x[1].est, x[1].lst), schedule))
        return optimize.minimize(self.to_minimize, objective, bounds=bounds, tol=1.0, method="L-BFGS-B")

    def to_minimize(self, schedule):
        indices = list(map(lambda x: int(max(self.producer.schedule[x][1].load_profile.index.values.tolist()) + schedule[x]), range(0, len(schedule))))
        indices.sort()

        consumed_t = defaultdict(float)
        produced_t = defaultdict(float)
        consumed = 0
        produced = 0
        penalty = 0
        for t in range(max(indices)):
            for i, j in enumerate(schedule):
                c = load_profile_utils.power(self.producer.schedule[i][1].load_profile, t)
                consumed_t[t + j] += c
                consumed += c
            p = load_profile_utils.power(self.producer.prediction, t)

            produced_t[t] += produced
            produced += p


        for t, c in consumed_t.items():
            p = produced_t[t]
            penalty += p - c

        score = math.fabs(produced - consumed) + math.fabs(penalty * 1)
        return score
