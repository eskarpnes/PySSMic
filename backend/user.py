from .device import Device


class User():
    def __init__(self, userId):
        self.userId = userId
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

    def remove_device(self, deviceId):
        for device in self.devices:
            if(device.id == deviceId):
                self.devices.remove(device)
