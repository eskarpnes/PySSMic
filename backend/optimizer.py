import itertools
import logging
import math
from collections import defaultdict
from itertools import chain
from random import randint, random
from typing import List

import numpy as np
import pandas as pd
from scipy import optimize
import util.optimizer_utils as utils


class Optimizer:
    def __init__(self, producer, options):
        self.producer = producer
        self.options = options
        self.algorithm = options["algo"]
        self.logger = logging.getLogger("src.Optimizer")
        self.differentiated_loads = []
        self.differentiated_production = None
        self.penalty_factor = 1.0
        self.min_objective_value = float('inf')

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self):
        if self.algorithm == 'basinhopping':
            schedule_times, should_keep = self.basinhopping()

        elif self.algorithm == '50/50':
            schedule_times, should_keep = self.fifty_fifty()

        else:
            should_keep = [True for x in range(len(self.producer.schedule))]
            schedule_times = [s['job'].scheduled_time for s in self.producer.schedule]

        return schedule_times, should_keep

    def basinhopping(self):
        indices = list(set(chain.from_iterable(
            map(lambda x: self.producer.schedule[x]['job'].load_profile.index.values.tolist(),
                range(0, len(self.producer.schedule))))))
        indices.sort()

        # Interpolate and differentiate load profiles before optimization.
        self.differentiated_production = utils.differentiate_and_interpolate(self.producer.prediction, indices)
        self.differentiated_loads = []
        for s in self.producer.schedule:
            self.differentiated_loads.append(utils.differentiate(s['job'].load_profile))

        tol = self.options["tol"] if "tol" in self.options else 1000.0
        eps = self.options["eps"] if "eps" in self.options else 0.001
        now = self.producer.manager.clock.now
        bounds = [(max(s['job'].est, now), s['job'].lst) for s in self.producer.schedule]
        x0 = np.array([randint(b[0], b[1]) for b in bounds])
        kwargs = dict(method="L-BFGS-B", bounds=bounds, options=dict(eps=eps), tol=tol)

        # The Basin-hopping algorithm is good at finding global minimums.
        result = optimize.basinhopping(func=self.objective_function, x0=x0, minimizer_kwargs=kwargs)
        objective_value = result.fun
        schedule_times = list([int(round(e)) for e in result.x])

        should_keep = [True for x in range(len(self.producer.schedule))]

        if objective_value > self.min_objective_value:
            should_keep[-1] = False
        else:
            self.min_objective_value = objective_value

        return schedule_times, should_keep

    def fifty_fifty(self):
        should_keep = [True for x in range(len(self.producer.schedule))]
        if random() < 0.5:
            should_keep[-1] = False
        schedule_times = [s['job'].scheduled_time for s in self.producer.schedule]
        return schedule_times, should_keep

    def objective_function(self, schedule: List[float]):
        consumed = defaultdict(float)

        for i, load in enumerate(self.differentiated_loads):
            for t, p in load.items():
                if not math.isnan(schedule[i]):
                    offset = schedule[i]
                    consumed[int(round(t + offset))] += p

        penalty = 0
        diff = 0
        ts = list(consumed.keys())
        produced = utils.differentiate_and_interpolate(self.producer.prediction, ts)
        ts.extend(list(produced.index.values))
        ts = sorted(ts)
        for i, t in enumerate(ts):
            if i == 0:
                delta = ts[1] - ts[0]
            else:
                delta = t - ts[i - 1]
            p = produced[t]
            c = consumed[t]
            diff_t = abs(p - c) * delta
            diff += diff_t
            if c > p:
                penalty += diff_t

        return diff + penalty

