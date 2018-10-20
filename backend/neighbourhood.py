import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.house import House


class Neighbourhood():
    def __init__(self, n_id):
        self.id = n_id
        self.houses = []

    def add_house(self, house):
        self.houses.append(house)

    def remove_house(self, house):
        self.houses.remove(house)

    def get_houses(self):
        return self.houses

    def get_house(self, house_id):
        for house in self.houses:
            if(house.get_id() == house_id):
                return house

    # delete
    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__)

    def __str__(self):
        return str(self.id)
