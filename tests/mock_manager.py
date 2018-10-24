from .mock_clock import MockClock

class MockManager:
    def __init__(self):
        self.clock = MockClock()
