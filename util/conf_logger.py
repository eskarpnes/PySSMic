import logging.config
import sys

logger = logging.getLogger("src")

# Creates a logger for sys.stdout
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Change this to upper/lower log level (DEBUG - INFO - WARNING - ERROR)
logger.setLevel(logging.DEBUG)
