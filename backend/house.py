import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.user import User
'''
    All houses has only 1 user
    '''


class House():
    def __init__(self, house_id):
        self.id = house_id
        self.users = []

    def findDeviceById(self, deviceId):
        for device in self.users[0].devices:
            if device.id == deviceId:
                return device

    def __str__(self):
        return str(self.id)
