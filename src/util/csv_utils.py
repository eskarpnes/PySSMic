import csv
import os
from definitions import ROOT_DIR

from src.backend.consumerEvent import ConsumerEvent
from src.backend.producerEvent import ProducerEvent
from src.backend.load import Load
from src.backend.prediction import Prediction


# Functions to convert a csv file into a list of objects of their respective type.
def list_consumer_event_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            row = row[0].split(";")
            csv_list.append(ConsumerEvent(row[0], row[1], row[2], row[3], row[4]))
    return csv_list


def list_producer_event_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            row = row[0].split(";")
            csv_list.append(ProducerEvent(row[0], row[1], row[2]))
    return csv_list


def list_load_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            row = row[0].split(" ")
            csv_list.append(Load(row[0], row[1], csvfile))
    return csv_list


def list_prediction_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            row = row[0].split(" ")
            csv_list.append(Prediction(row[0], row[1], csvfile))
    return csv_list


# Used for testing
def test_list(csv_list):
    for e in csv_list:
        print(e)

# NOTE: - Load and Prediction objects currently derive csvName (And thereby Ids) from the FILE PATH parameter.
#       - ProducerEvent Ids can be derived from csvName. Is id parameter redundant? / csvName always same format?

# Testing:
# test_list(list_consumer_event_objects(os.path.join(ROOT_DIR, "input", "test", "consumer_event.csv")))
# test_list(list_producer_event_objects(os.path.join(ROOT_DIR, "input", "test", "producer_event.csv")))
# test_list(list_load_objects(os.path.join(ROOT_DIR, "input", "test", "loads", "96.csv")))
# test_list(list_prediction_objects(os.path.join(ROOT_DIR, "input", "test", "predictions", "57_220_1.csv")))
