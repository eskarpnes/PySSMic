class ProducerEvent:
    timestamp = 0
    csvName = ""
    houseId = 0
    producerId = 0
    id = 0

    def __init__(self, timestamp, ids, csv_name):
        self.timestamp = int(timestamp)
        self.csvName = csv_name
        # ids_list = list(map(int, ids.replace("[", "").replace("]", "").replace("pv_producer", "").split(":")))
        # self.houseId = int(ids_list[0])
        # self.producerId = int(ids_list[1])
        ids_list = csv_name.split("_")
        self.houseId = int(ids_list[0])
        self.producerId = int(ids_list[1])
        self.id = int(ids_list[2].split(".")[0])

    def __str__(self):
        return "timestamp %r, csvName %r, houseId %r, producerId %r, Id %r" %\
               (self.timestamp, self.csvName, self.houseId, self.producerId, self.id)
