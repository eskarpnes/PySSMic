from enum import Enum


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

    def to_message(self):
        return {
            'est': self.est,
            'lst': self.lst,
            'load_profile': self.load_profile
        }
