import os

from definitions import ROOT_DIR


class MockClock:
    def __init__(self):
        self.now = 0


class MockManager:
    def __init__(self):
        self.clock = MockClock()

    def register_contract(self, job):
        pass

class MockSimulator:
    def __init__(self):
        self.neighbourhood = MockClock()
        self.DATA_DIR = ""

    def register_contract(self, job):
        pass
