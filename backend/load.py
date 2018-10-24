class Load:
    elapsedTime = 0
    powerUsage = 0.0
    csvName = ""
    id = 0
    isBackgroundLoad = None

    def __init__(self, elapsed_time, power_usage, csv_path):
        self.elapsedTime = int(elapsed_time)
        self.powerUsage = float(power_usage)
        self.csvName = csv_path.split("\\")[-1]     # csvName currently depends on file path (!!)
        self.id = int(self.csvName.split(".")[0])
        self.isBackgroundLoad = "back" in self.csvName

    def __str__(self):
        return "elapsedTime %r, powerUsage %r, csvName %r, id %r, isBackgroundLoad %r" %\
               (self.elapsedTime, self.powerUsage, self.csvName, self.id, self.isBackgroundLoad)
