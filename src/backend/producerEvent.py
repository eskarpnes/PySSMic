class ProducerEvent:
    timestamp = 0
    panelID = None     # [houseId, producerId]
    csvName = ""

    def __init__(self, timestamp, panel_id, csv_name):
        self.timestamp = int(timestamp)
        self.panelID = list(map(int, panel_id.replace("[", "").replace("]", "").replace("pv_producer", "").split(":")))
        self.csvName = csv_name
