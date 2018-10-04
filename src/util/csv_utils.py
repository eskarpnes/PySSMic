import csv
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
            csv_list.append(ConsumerEvent(row[0], row[1], row[2], row[3], row[4]))
    return csv_list


def list_producer_event_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(ProducerEvent(row[0], row[1], row[2]))
    return csv_list


def list_load_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(Load(row[0], row[1], csvfile))
    return csv_list


def list_prediction_objects(csvfile):
    csv_list = []
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(Prediction(row[0], row[1], csvfile))
    return csv_list