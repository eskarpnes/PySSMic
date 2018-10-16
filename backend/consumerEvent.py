class ConsumerEvent:
    regTime = 0
    startTime = 0
    latestTime = 0
    csvName = ""
    houseId = 0
    consumerId = 0
    id = 0

    def __init__(self, reg_time, start_time, latest_time, ids, csv_name):
        self.regTime = int(reg_time)
        self.startTime = int(start_time)
        self.latestTime = int(latest_time)
        self.csvName = csv_name
        ids_list = list(map(int, ids.replace("[", "").replace("]", "").split(":")))
        self.houseId = int(ids_list[0])
        self.consumerId = int(ids_list[1])
        self.id = int(ids_list[2])

    def __str__(self):
        return "RegTime %r, StartTime %r, latestTime %r, csvName %r, houseId %r, consumerId %r, id %r" %\
               (self.regTime, self.startTime, self.latestTime, self.csvName, self.houseId, self.consumerId, self.id)
