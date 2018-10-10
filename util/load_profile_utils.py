import pandas as pd


def power(load_profile, t):
    if t in load_profile.index.values:
        return load_profile[t]
    elif t < min(load_profile.index.values):
        return 0.0
    elif t > max(load_profile.index.values):
        return 0.0
    else:
        appended = load_profile.append(pd.Series(data=[float('nan')], index=[t])).sort_index()
        interpolated = appended.interpolate(method='barycentric')
        return interpolated[t]
