from enum import Enum
import pandas as pd


class JobStatus(Enum):
    running = 'RUNNING'
    active = 'ACTIVE'
    cancelled = 'CANCELLED'
    created = 'CREATED'
    future = 'FUTURE'


class Job:

    def __init__(self, est, lst, load_profile):
        self.est = est
        self.lst = lst
        self.load_profile = load_profile

    def __eq__(self, other):
        return self.est == other.est and \
               self.lst == other.lst and \
               self.load_profile.equals(other.load_profile)

    def __str__(self):
        return "\nest: " + str(self.est) + "\nlst: " + str(self.lst)

    def to_message(self):
        return {
            'est': self.est,
            'lst': self.lst,
            'load_profile': self.load_profile
        }

    def normalize_time(self, offset):
        self.est = self.est-offset
        self.lst = self.lst-offset

    def power(self, t):
        if t in self.load_profile.index.values:
            return self.load_profile[t]
        elif t < 0:
            return 0
        elif t > max(self.load_profile.index.values):
            return self.load_profile[self.load_profile.index[-1]]
        else:
            appended = self.load_profile.append(pd.Series(data=[float('nan')], index=[t])).sort_index()
            interpolated = appended.interpolate(method='barycentric')
            return interpolated[t]

