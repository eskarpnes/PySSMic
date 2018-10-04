import os
from src.backend.job import Job
import pandas as pd
from definitions import ROOT_DIR


def job_from_consumer_event(csv_line):
    split = csv_line.split(";")
    est = int(split[1])
    lst = int(split[2])
    load_profile_name = split[4]
    load_profile_path = os.path.join(ROOT_DIR, "input/loads/" + load_profile_name)
    load_profile_csv = open(load_profile_path, "r").read()
    load_profile = load_profile_from_csv(load_profile_csv)
    return Job(est, lst, load_profile)


def load_profile_from_csv(csv):
    split_by_new_line = filter(lambda x: len(x) > 2, csv.split("\n"))
    parsed = [[float(cell) for cell in line.split(" ")] for line in split_by_new_line]
    timestamps = map(lambda x: x[0], parsed)
    values = map(lambda x: x[1], parsed)
    return pd.Series(data=values, index=timestamps)


def get_events_from_csv(filename):
    events = []
    events_csv_filepath = os.path.join(ROOT_DIR, "input", filename)
    events_csv = open(events_csv_filepath, "r").read()
    event_lines = events_csv.split("\n")
    for line in event_lines:
        if line is not "":
            timestamp = line.split(";")[0]
            events.append({
                "timestamp": timestamp,
                "job": job_from_consumer_event(line)
            })
    print(events)
    return events


if __name__ == "__main__":
    get_events_from_csv("consumer_event.csv")
