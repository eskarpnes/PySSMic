class LoadProfile:

    def __init__(self, timestamps, loads):
        self.timestamps = timestamps
        self.loads = loads

    def __eq__(self, other):
        return self.timestamps == other.timestamps and self.loads == other.loads

