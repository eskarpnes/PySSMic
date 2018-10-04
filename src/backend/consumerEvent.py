class ConsumerEvent:
    regTime = 0
    startTime = 0
    latestTime = 0
    deviceID = None     # [houseId, deviceId, Id]
    csvName = ""

    def __init__(self, reg_time, start_time, latest_time, device_id, csv_name):
        self.regTime = int(reg_time)
        self.startTime = int(start_time)
        self.latestTime = int(latest_time)
        self.deviceID = list(map(int, device_id.replace("[", "").replace("]", "").split(":")))
        self.csvName = csv_name
