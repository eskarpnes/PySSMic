import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from backend.device import Device


class User():
    def __init__(self, userId):
        self.userId = userId
        self.devices = []

    def get_id(self):
        return self.userId

    def add_device(self, device):
        self.devices.append(device)

    def remove_device(self, device):
        self.devices.remove(device)
