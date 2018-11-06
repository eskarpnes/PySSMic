import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.house import House


class Neighbourhood():
    def __init__(self, n_id):
        self.id = n_id
        self.houses = []

    def findHouseById(self, houseId):
        for house in self.houses:
            if house.id == houseId:
                return house
        return None

    def nextHouseId(self):
        return self.houses[-1].id + 1
    # delete

    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    def __str__(self):
        return str(self.id)
