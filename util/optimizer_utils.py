import pandas as pd
import numpy as np


def differentiate_and_interpolate(series, indices):
    interpolated = interpolate(series, indices)
    derivative = differentiate(interpolated)
    return derivative


def differentiate(series):
    x = series.index
    y = series.values
    dy = np.zeros(y.shape, np.float)
    dy[0:-1] = np.diff(y) / np.diff(x)
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])

    return pd.Series(index=x, data=dy)


def interpolate(series, indices):
    not_included = [t for t in indices if t not in series.index.values]
    with_new_indices = series.append(
        pd.Series(index=not_included, data=[np.nan for x in range(len(not_included))])).sort_index()
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
