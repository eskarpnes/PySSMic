import logging.config
import sys

logger = logging.getLogger("src")

# Creates a logger for sys.stdout
handler = logging.StreamHandler(stream=sys.stdout)
fileHandler = logging.FileHandler("log.txt", mode='w')
logger.addHandler(handler)
logger.addHandler(fileHandler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

# Change this to upper/lower log level (DEBUG - INFO - WARNING - ERROR)
logger.setLevel(logging.DEBUG)
