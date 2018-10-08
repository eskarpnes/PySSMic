import os
import math
from src.backend.job import Job
import pandas as pd
from definitions import ROOT_DIR


def job_from_consumer_event(csv_line, config_name):
    split = csv_line.split(";")
    est = int(split[1])
    lst = int(split[2])
    load_profile_name = split[4]
    load_profile_path = os.path.join(ROOT_DIR, "input", config_name, "loads", load_profile_name)
    load_profile_csv = open(load_profile_path, "r").read()
    load_profile = load_profile_from_csv(load_profile_csv)
    return Job(est, lst, load_profile)


def load_profile_from_csv(csv):
    split_by_new_line = filter(lambda x: len(x) > 2, csv.split("\n"))
    parsed = [[float(cell) for cell in line.split(" ")] for line in split_by_new_line]
    timestamps = map(lambda x: x[0], parsed)
    values = map(lambda x: x[1], parsed)
    return pd.Series(data=values, index=timestamps)


def get_events_from_csv(config_name):
    events = []
    events_csv_filepath = os.path.join(ROOT_DIR, "input", config_name, "consumer_event.csv")
    events_csv = open(events_csv_filepath, "r").read()
    event_lines = events_csv.split("\n")
    for line in event_lines:
        if line is not "":
            timestamp = line.split(";")[0]
            events.append({
                "timestamp": timestamp,
                "job": job_from_consumer_event(line, config_name)
            })
    return events


def prediction_profile_from_csv(prediction_csv):
    split_by_new_line = prediction_csv.split("\n")
    timestamps = []
    values = []
    for line in split_by_new_line:
        if line is not "":
            split_line = line.split(" ")
            timestamps.append(split_line[0])
            values.append(split_line[1])
    return pd.Series(data=values, index=timestamps)


def prediction_from_producer_event(csv_line, config_name):
    split = csv_line.split(";")
    prediction_file = split[2]
    prediction_profile_path = os.path.join(ROOT_DIR, "input", config_name, "predictions", prediction_file)
    prediction_csv = open(prediction_profile_path, "r").read()
    prediction_profile = prediction_profile_from_csv(prediction_csv)
    return prediction_profile


def get_predictions_from_csv(config_name):
    predictions = []
    predictions_csv_filepath = os.path.join(ROOT_DIR, "input", config_name, "producer_event.csv")
    predictions_csv = open(predictions_csv_filepath, "r").read()
    predictions_lines = predictions_csv.split("\n")
    for line in predictions_lines:
        if line is not "":
            timestamp = line.split(";")[0]
            predictions.append({
                "timestamp": timestamp,
                "prediction": prediction_from_producer_event(line, config_name)
            })
    return predictions


def normalize_times(events, predictions):
    # Finding the time of the first event
    min_time = math.inf
    for event in events:
        if int(event["timestamp"]) < min_time:
            min_time = int(event["timestamp"])
    for prediction in predictions:
        if int(prediction["timestamp"]) < min_time:
            min_time = int(prediction["timestamp"])

    # Normalizing every timestamp
    for i in range(len(events)):
        events[i]["timestamp"] = int(events[i]["timestamp"]) - min_time
        events[i]["job"].normalize_time(min_time)
    for i in range(len(predictions)):
        predictions[i]["timestamp"] = int(predictions[i]["timestamp"]) - min_time
        predictions[i]["prediction"] = predictions[i]["prediction"].rename(lambda x: int(x)-min_time)
    return events, predictions


if __name__ == "__main__":
    events = get_events_from_csv("test")
    predictions = get_predictions_from_csv("test")
    events, predictions = normalize_times(events, predictions)
    print(events)
    print(predictions)
