class MockClock:
    def __init__(self):
        self.now = 0


class MockManager:
    def __init__(self):
        self.clock = MockClock()
