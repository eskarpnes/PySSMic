class Job:

    def __init__(self, est, lst, load_profile):
        self.est = est
        self.lst = lst
        self.load_profile = load_profile

    def __eq__(self, other):
        return self.est == other.est and \
               self.lst == other.lst and \
               self.load_profile == other.load_profile
