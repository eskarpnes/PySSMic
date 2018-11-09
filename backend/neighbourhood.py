import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


class Neighbourhood():
    def __init__(self, n_id):
        self.id = n_id
        self.houses = []

    def __str__(self):
        return str(self.id)

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


class House():
    def __init__(self, house_id):
        self.id = house_id
        self.users = []

    def findDeviceById(self, deviceId):
        for device in self.users[0].devices:
            if device.id == deviceId:
                return device
        return None

    def __str__(self):
        return str(self.id)


class User():
    def __init__(self, userId):
        self.id = userId
        self.devices = []

    def get_id(self):
        return self.id

    def add_device(self, device):
        self.devices.append(device)

    def remove_device(self, device):
        self.devices.remove(device)

    def __str__(self):
        return str(self.id)


import datetime


class Device():
    def __init__(self, devId, name, template, devType):
        self.id = devId
        self.name = name
        self.template = template
        self.type = devType
        self.loadProfile = None
        self.events = []
        self.weatherPredictions1 = None
        self.weatherPredictions2 = None
        self.weatherPredictions3 = None
        self.weatherPredictions4 = None

    def __str__(self):
        return str(self.name)


class Event():
    def __init__(self, device, time, est, lst):
        self.device = device
        self.timestamp = time
        self.est = est
        self.lst = lst

    def __str__(self):
        return self.unixToString(self.timestamp) + " event for " + self.device.name + " est " + self.unixToString(self.est) + " lst " + self.unixToString(self.lst)

    def unixToString(self, time):
        return datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
