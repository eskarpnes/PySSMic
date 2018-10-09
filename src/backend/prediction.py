class Prediction:
    timestamp = 0
    powerProduction = 0.0
    csvName = ""
    houseId = 0
    producerId = 0
    id = 0

    def __init__(self, timestamp, power_production, csv_path):
        self.timestamp = int(timestamp)
        self.powerProduction = float(power_production)
        self.csvName = csv_path.split("\\")[-1]  # csvName currently depends on file path (!!)
        ids = self.csvName.split("_")
        self.houseId = int(ids[0])
        self.producerId = int(ids[1])
        self.id = int(ids[2].split(".")[0])

    def __str__(self):
        return "timestamp %r, powerProduction %r, csvName %r, houseID %r, producerId %r, predictionID %r" %\
               (self.timestamp, self.powerProduction, self.csvName, self.houseId, self.producerId, self.id)
