class Prediction:
    timestamp = 0
    powerProduction = 0.0
    csvName = ""
    houseID = 0
    panelID = 0
    predictionID = 0

    def __init__(self, timestamp, power_production, csv_name):
        self.timestamp = timestamp
        self.powerProduction = power_production
        self.csvName = csv_name
        ids = csv_name.split("_")
        self.houseID = ids[0]
        self.panelID = ids[1]
        self.predictionID = ids[2]
