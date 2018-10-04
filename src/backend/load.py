class Load:
    elapsedTime = 0
    powerUsage = 0.0
    csvName = ""
    isBackgroundLoad = None

    def __init__(self, elapsed_time, power_usage, csv_name):
        self.elapsedTime = elapsed_time
        self.powerUsage = power_usage
        self.csvName = csv_name
        self.isBackgroundLoad = "back" in csv_name
