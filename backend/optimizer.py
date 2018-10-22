import itertools
import logging
from itertools import chain
from typing import List

import numpy as np
import pandas as pd


class Optimizer:
    def __init__(self, producer):
        self.producer = producer
        self.logger = logging.getLogger("src.Optimizer")
        self.differentiated_loads = []
        self.differentiated_production = None
        self.indices = []
        self.penalty_factor = 1.0

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self):
        indices = list(set(chain.from_iterable(
            map(lambda x: self.producer.schedule[x][1].load_profile.index.values.tolist(),
                range(0, len(self.producer.schedule))))))
        indices.sort()
        self.indices = indices

        # Interpolate and differentiate load profiles before optimization.
        self.differentiated_production = self.differentiate_and_interpolate(self.producer.prediction, indices)
        for s in self.producer.schedule:
            self.differentiated_loads.append(self.differentiate_and_interpolate(s[1].load_profile, indices))

        objective = np.zeros(len(self.producer.schedule))
        # return optimize.minimize(self.to_minimize, objective, tol=1.0, method="trust-ncg")
        configs = list(map(list, itertools.product([0, 1], repeat=len(self.differentiated_loads))))
        return self.recursive_binary_optimizer(configs, float('inf'), configs[0])

    def to_minimize(self, schedule: List[float]):
        produced = []
        consumed = []

        for t in self.indices:
            consumed_t = 0
            for i, load in enumerate(self.differentiated_loads):
                if schedule[i] > 0:
                    consumed_t += load[t]

            consumed.append(consumed_t)
            produced.append(self.differentiated_production[t])

        penalty = 0
        diff = 0
        for p, c in zip(produced, consumed):
            diff_t = abs(p - c)
            diff += diff_t
            if c > p:
                penalty += diff_t

        return diff, penalty

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
        indices = list(series.index)
        values = list(series.values)
        derivative = []
        for i in range(1, len(indices) + 1):
            if i >= len(indices):
                derivative.insert(0, values[0])
            else:
                p0 = values[i - 1]
                t0 = indices[i - 1]
                p1 = values[i]
                t1 = indices[i]

                d = (p1 - p0)
                derivative.append(d)

        return pd.Series(index=indices, data=derivative)

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
