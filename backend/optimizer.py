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
    def __init__(self, producer, algorithm='basinhopping'):
        self.producer = producer
        self.algorithm = algorithm
        self.logger = logging.getLogger("src.Optimizer")
        self.differentiated_loads = []
        self.differentiated_production = None
        self.penalty_factor = 1.0
        self.previous_objective_score = float('inf')

    # The main function that optimizes the schedule. How the schedule and job should be implemented is up for discussion
    def optimize(self, tol=1000.0, eps=0.001) -> (List[float], List[bool]):
        dup = len(set([x['job'].id for x in self.producer.schedule])) < len(self.producer.schedule)

        indices = list(set(chain.from_iterable(
            map(lambda x: self.producer.schedule[x]['job'].load_profile.index.values.tolist(),
                range(0, len(self.producer.schedule))))))
        indices.sort()

        # Interpolate and differentiate load profiles before optimization.
        self.differentiated_production = self.differentiate_and_interpolate(self.producer.prediction, indices)
        self.differentiated_loads = []
        for s in self.producer.schedule:
            self.differentiated_loads.append(self.differentiate(s['job'].load_profile))

        if self.algorithm == 'basinhopping':
            now = self.producer.manager.clock.now
            bounds = [(max(s['job'].est, now), s['job'].lst) for s in self.producer.schedule]
            x0 = np.array([randint(b[0], b[1]) for b in bounds])
            # TODO: Find reasonable default values for eps and tol, and let frontend choose
            kwargs=dict(method="L-BFGS-B", bounds=bounds, options=dict(eps=eps), tol=tol)

            # The Basin-hopping algorithm is good at finding global minimums.
            result = optimize.basinhopping(func=self.to_minimize, x0=x0, minimizer_kwargs=kwargs)
            x = list([int(round(e)) for e in result.x])
            self.logger.debug("x0:" + str(x0) + ", score: " + str(self.to_minimize(x0)))
            self.logger.debug("x1:" + str(np.array(x)) + ", score: " + str(result.fun))
            should_keep = [True for x in range(len(bounds))]
            
            if result.fun > self.previous_objective_score:
                should_keep[-1] = False
                return x, should_keep
            else:
                self.previous_objective_score = result.fun
                return x, should_keep

    def to_minimize(self, schedule: List[float]):
        consumed = defaultdict(float)

        for i, load in enumerate(self.differentiated_loads):
            for t, p in load.items():
                if not math.isnan(schedule[i]):
                    offset = schedule[i]
                    consumed[int(round(t + offset))] += p

        penalty = 0
        diff = 0
        ts = list(consumed.keys())
        produced = self.differentiate_and_interpolate(self.producer.prediction, ts)
        ts.extend(list(produced.index.values))
        ts = sorted(ts)
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

        return diff + penalty

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
        with_new_indices = series.append(pd.Series(index=not_included, data=[np.nan for x in range(len(not_included))])).sort_index()
        interpolated = with_new_indices.interpolate(method="linear")

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
