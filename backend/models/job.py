import random
from enum import Enum
import pandas as pd

class Job:

    def __init__(self, id, est, lst, load_profile):
        self.id = id
        self.est = est
        self.lst = lst
        self.load_profile = load_profile
        self.scheduled_time = random.randint(est, lst)

    def __eq__(self, other):
        return self.est == other.est and \
               self.lst == other.lst and \
               self.load_profile.equals(other.load_profile)

    def normalize_time(self, offset):
        self.est = self.est-offset
        self.lst = self.lst-offset
        self.scheduled_time = self.scheduled_time-offset
