import pandas as pd
import numpy as np


def differentiate_and_interpolate(series, indices):
    interpolated = interpolate(series, indices)
    differentiated = differentiate(interpolated)
    return differentiated


def differentiate(series):
    """Numerically differentiate series"""
    return series.diff().fillna(0.0)


def interpolate(series, indices):
    """Linearly interpolate series on indices."""
    not_included = [t for t in indices if t not in series.index.values]
    new_indices_series = pd.Series(index=not_included, data=[np.nan]*len(not_included))
    with_new_indices = series.append(new_indices_series).sort_index()
    interpolated = with_new_indices.interpolate(method="linear")

    # We want the values on the indices before the (originally) first index to be equal to the first value. Similarly,
    # we want the values after the (originally) last index to be equal to the last value.
    min_index = min(series.index.values)
    max_index = max(series.index.values)
    start_value = series.data[0]
    end_value = series.data[-1]

    new_values = []
    for t, p in interpolated.items():
        if t < min_index:
            new_values.append(start_value)
        elif t > max_index:
            new_values.append(end_value)
        else:
            new_values.append(p)

    new_series = pd.Series(data=new_values, index=interpolated.index)

    return new_series
