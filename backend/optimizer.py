import itertools
import logging
import math
from collections import defaultdict
from itertools import chain
from random import randint
from typing import List

import numpy as np
import pandas as pd
from scipy import optimize


class Optimizer:
    def __init__(self, producer, algorithm='bounded'):
        self.producer = producer
        self.algorithm = algorithm
        self.logger = logging.getLogger("src.Optimizer")
        self.differentiated_loads = []
        self.differentiated_production = None
        self.indices = []
        self.penalty_factor = 1.0
        self.previous_objective_score = float('inf')

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self) -> (List[float], List[bool]):
        indices = list(set(chain.from_iterable(
            map(lambda x: self.producer.schedule[x][1].load_profile.index.values.tolist(),
                range(0, len(self.producer.schedule))))))
        indices.sort()
        self.indices = indices

        # Interpolate and differentiate load profiles before optimization.
        self.differentiated_production = self.differentiate_and_interpolate(self.producer.prediction, indices)
        print("length: %d" %len(self.producer.schedule))
        self.differentiated_loads = []
        for s in self.producer.schedule:
            self.differentiated_loads.append(self.differentiate_and_interpolate(s[1].load_profile, indices))

        if self.algorithm == 'bounded':
            bounds = [(s[1].est, s[1].lst) for s in self.producer.schedule]
            x0 = np.array([randint(b[0], b[1]) for b in bounds])
            # x0 = [0, 2, 4, 6, 6]
            self.logger.debug("x0:" + str(x0))
            options=dict(eps=1.0)
            result = optimize.minimize(fun=self.to_minimize, x0=x0, bounds=bounds, method="SLSQP", options=options)
            should_keep = [True for x in range(len(bounds))]
            x = list([int(round(e)) for e in result.x])
            if result.fun > self.previous_objective_score:
                should_keep[-1] = False
                return x, should_keep
            else:
                return x, should_keep

        elif self.algorithm == 'alpha_beta':
            configs = list(map(list, itertools.product([0, 1], repeat=len(self.differentiated_loads))))
            return self.recursive_binary_optimizer(configs, float('inf'), configs[0])

    def to_minimize(self, schedule: List[float]):
        consumed = defaultdict(float)

        for t in self.indices:
            for i, load in enumerate(self.differentiated_loads):
                consumed[int(round(t + schedule[i]))] += load[t]


        penalty = 0
        diff = 0
        all_indices = list(consumed.keys())
        all_indices.extend(self.indices)
        all_indices.extend(self.producer.prediction.index.values)
        ts = sorted(list(set(all_indices)))
        produced = self.differentiate_and_interpolate(self.producer.prediction, ts)
        for i, t in enumerate(ts):
            if i == 0:
                delta = ts[1] - ts[0]
            else:
                delta = t-ts[i-1]
            p = produced[t]
            c = consumed[t]
            diff_t = abs(p - c) * delta
            diff += diff_t
            if c > p:
                penalty += diff_t

        return diff

    def binary_optimzier(self):
        configs = map(list, itertools.product([0, 1], repeat=len(self.differentiated_loads)))
        min_config = None
        min_config_value = float('inf')
        for c in configs:
            diff, penalty = self.to_minimize(c)
            if diff < min_config_value:
                min_config_value = diff + penalty
                min_config = c
        return min_config

    def recursive_binary_optimizer(self, configs, min_value, min_config):
        if len(configs) == 0:
            return min_config
        current_config = configs[0]
        diff, penalty = self.to_minimize(current_config)

        if penalty > min_value:
            config_indices = [i for i, x in enumerate(current_config) if x == 1.0]
            new_configs = list(filter(lambda c: not all(map(lambda i: c[i], config_indices)), configs))
            return self.recursive_binary_optimizer(new_configs, min_value, min_config)

        elif penalty + diff < min_value:
            return self.recursive_binary_optimizer(configs[1:], penalty + diff, current_config)

        else:
            return self.recursive_binary_optimizer(configs[1:], min_value, min_config)

    def differentiate_and_interpolate(self, series: pd.Series, indices: List[int]):
        interpolated = self.interpolate(series, indices)
        derivative = self.differentiate(interpolated)
        return derivative

    def differentiate(self, series: pd.Series):
        x = series.index
        y = series.values
        dy = np.zeros(y.shape, np.float)
        dy[0:-1] = np.diff(y)/np.diff(x)
        dy[-1] = (y[-1] - y[-2])/(x[-1] - x[-2])

        return pd.Series(index=x, data=dy)

    def interpolate(self, series: pd.Series, indices: List[int]):
        not_included = list(filter(lambda t: t not in series.index.values, indices))
        with_new_indices = series.append(pd.Series(index=not_included, data=[np.nan for x in range(len(not_included))]))
        interpolated = with_new_indices.interpolate(method="barycentric").sort_index()

        min_index = min(series.index.values)
        max_index = max(series.index.values)
        start_value = series.data[0]
        end_value = series.data[-1]

        for t, p in interpolated.items():
            if t < min_index:
                interpolated.update(pd.Series(data=[start_value], index=[t]))
            elif t > max_index:
                interpolated.update(pd.Series(data=[end_value], index=[t]))

        return interpolated
