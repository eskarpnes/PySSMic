import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


class Neighbourhood:
    def __init__(self, n_id):
        self.id = n_id
        self.houses = []

    def __str__(self):
        return str(self.id)

    def find_house_by_id(self, house_id):
        for house in self.houses:
            if house.id == house_id:
                return house
        return None

    def nextHouseId(self):
        return self.houses[-1].id + 1

    def to_json(self):
        return json.dumps(self, default=lambda x: x.__dict__)


class House:
    def __init__(self, house_id):
        self.id = house_id
        self.users = []

    def find_device_by_id(self, device_id):
        for device in self.users[0].devices:
            if device.id == device_id:
                return device
        return None

    def __str__(self):
        return str(self.id)


class User:
    def __init__(self, user_id):
        self.id = user_id
        self.devices = []

    def get_id(self):
        return self.id

    def add_device(self, device):
        self.devices.append(device)

    def remove_device(self, device):
        self.devices.remove(device)

    def __str__(self):
        return str(self.id)


class Device:
    def __init__(self, dev_id, name, template, dev_type):
        self.id = dev_id
        self.name = name
        self.template = template
        self.type = dev_type
        self.load_profile = None
        self.events = []
        self.weather_prediction1 = None
        self.weather_prediction2 = None
        self.weather_prediction3 = None
        self.weather_prediction4 = None

    def __str__(self):
        return str(self.name)


class Event:
    def __init__(self, time, est, lst):
        self.timestamp = time
        self.est = est
        self.lst = lst

    def __str__(self):
        return (self.timestamp)
