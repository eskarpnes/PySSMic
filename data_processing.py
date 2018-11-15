import pandas as pd
import numpy as np
import pickle
import os.path
from datetime import datetime
from definitions import ROOT_DIR
import statistics


def open_file(file_name):
    path = os.path.join(ROOT_DIR, "results", file_name)
    print("opening " + path)
    with open(path, "rb") as f:
        res = pickle.load(f)
        contracts = res[0]
        profiles = res[1]
    return contracts, profiles

# Contract methods
def get_contracts(file_name):
    contracts, profiles = open_file(file_name)
    return contracts


def get_contracts_for_house(house, contracts):
    output = []
    for contract in contracts:
        house_id = contract["job_id"].split(":")[0].replace("[", "").replace("]", "")
        if house_id == house:
            output.append(contract)
    return output


def rename_columns(contract):
    old_keys = ["id", "time", "time_of_agreement", "load_profile", "job_id", "producer_id"]
    new_keys = ["Contract ID", "Contract start time", "Contract agreement time", "Energy used (Wh)", "Consumer ID",
                "Producer ID"]
    for i in range(0, len(old_keys)):
        contract[new_keys[i]] = contract.pop(old_keys[i])
    return contract


# Profiles methods
def get_profiles(file_name):
    contracts, profiles = open_file(file_name)
    return profiles


def get_profiles_for_house(house, profiles):
    output = []
    for profile in profiles:
        house_id = profile.split(":")[0].replace("[", "").replace("]", "").replace("pv_producer", "")
        if house_id == house:
            output.append(profiles[profile])
    return output


# Peak to average ratio methods
# TODO: Rename to peak_to_average_ratio_consumption and change in results.py
def peak_to_average_ratio_consumption(contracts, interval=15):
    df = pd.DataFrame.from_dict(contracts)
    agreement_times = df["time"].tolist()
    x_consumption, y_consumption = change_index_time(df["load_profile"].tolist(), agreement_times)
    consumption_per_quarter = []
    quarter_consumption = 0.0
    for i in range(len(x_consumption)):
        quarter_consumption += y_consumption[i]
        if x_consumption[i] % interval == 0:
            consumption_per_quarter.append(quarter_consumption)
            quarter_consumption = 0
    average_consumption = np.mean(consumption_per_quarter)
    max_consumption = max(consumption_per_quarter)
    return max_consumption / average_consumption


def peak_to_average_ratio_production(profiles, interval=15):
    x_production, y_production = add_productions(profiles)
    if [] in [x_production, y_production]:
        return 0
    consumption_per_quarter = []
    quarter_consumption = 0.0
    for i in range(len(x_production)):
        quarter_consumption += y_production[i]
        if x_production[i] % interval == 0:
            consumption_per_quarter.append(quarter_consumption)
            quarter_consumption = 0
    average_consumption = np.mean(consumption_per_quarter)
    max_consumption = max(consumption_per_quarter)
    return max_consumption / average_consumption


# Production and consumption profile methods
def neighbourhood_execution_energy_over_time_average(contracts_input, profiles_input):
    output = []
    for i in range(len(contracts_input)):
        output.append(energy_over_time(contracts_input[i], list(profiles_input[i].values())))
    output_combined = average_list_with_lists(output)
    return output_combined


def neighbourhood_execution_energy_over_time(contracts_input, profiles_input):
    return energy_over_time(contracts_input, list(profiles_input.values()))


# Energy use for given run
def get_energy_use(run, simulation):
    contracts = open_file(simulation)[0]
    run_contracts = contracts[run]
    grid = 0
    pv = 0
    for contract in run_contracts:
        if contract.get("producer_id") == "grid":
            grid += contract.get("load_profile").values[-1]
        else:
            pv += contract.get("load_profile").values[-1]
    return [round(pv, 2), round(grid, 2), round(pv+grid, 2)]


# Standard deviation for given simulation
def get_standard_deviation(simulation):
    runs = get_contracts(simulation)
    total_local_consumption = []
    for contracts in runs:
        local_consumption = 0
        for contract in contracts:
            if contract["producer_id"] != "grid":
                local_consumption += contract["load_profile"].values[-1]
        total_local_consumption.append(local_consumption)
    # Returns [std, mean]
    if (len(total_local_consumption)) == 1:
        return [0, total_local_consumption[0]]
    return [round(statistics.stdev(total_local_consumption), 2), round(statistics.mean(total_local_consumption), 2)]


# Converting timestamp to readable date
def convert(timestamp):
    date = datetime.fromtimestamp(timestamp)
    return "Day {} {}".format(date.day, date.strftime("%H:%M:%S"))


"""----------------------HELPING METHODS----------------------"""


# Used in method: neighbourhood_execution_energy_over_time_average
def average_list_with_lists(list_of_listwithlists):
    list_of_lists = []
    transposed_list_of_listwithlists = map(list, zip(*list_of_listwithlists))
    for tl in transposed_list_of_listwithlists:
        transposed_tl = map(list, zip(*tl))
        temp_list = []
        for tll in transposed_tl:
            temp_list.append(np.mean(tll))
        list_of_lists.append(temp_list)
    return list_of_lists


# Used in method: peak_to_average_ratio_consumption
# Used in helping method: change_index_time
def change_index_time(energy_list, start_times):
    energy_series = pd.Series([0 for x in range(0, 86460, 60)], [x for x in range(0, 86460, 60)])
    for i in range(len(energy_list)):
        energy_values = energy_list[i]
        start_time = start_times[i]
        start_time = start_time // 60 * 60
        energy_values = energy_values.rename(lambda x: x + start_time)
        end_time = int(energy_values.index[-1])
        new_indexes = range(start_time, end_time + 60, 60)
        energy_values = energy_values.reindex(new_indexes)
        energy_values = energy_values.interpolate(method="linear")
        energy_values = energy_values.diff().fillna(0)
        energy_series = (energy_series + energy_values).fillna(energy_series).fillna(energy_values)
    energy_series = energy_series.rename(lambda x: x // 60)
    x_energy = energy_series.index.tolist()
    y_energy = energy_series.values.tolist()
    return [x_energy, y_energy]


# Used in method: peak_to_average_ratio_production
# Used in helping method: change_index_time
def add_productions(producer_profiles):
    if producer_profiles == []:
        return [], []
    produced_series = producer_profiles.pop(-1)
    for profile in producer_profiles:
        produced_series += profile
    end_time = int(produced_series.index[-1])
    new_indexes = range(0, end_time + 60, 60)
    produced_series = produced_series.reindex(new_indexes)
    produced_series = produced_series.interpolate(method="linear")
    produced_series = produced_series.diff().fillna(0)
    produced_series = produced_series.rename(lambda x: x // 60)
    x_production = produced_series.index.tolist()
    y_production = produced_series.values.tolist()
    # Returns energy (y) produced over time (x)
    return x_production, y_production


# Used in method: neighbourhood_execution_energy_over_time, neighbourhood_execution_energy_over_time_average
def energy_over_time(contracts, producer_profiles):
    local_contracts = []
    remote_contracts = []
    for contract in contracts:
        if contract["producer_id"] == "grid":
            remote_contracts.append(contract)
        else:
            local_contracts.append(contract)
    # Local consumption
    x_consumption_local, y_consumption_local = change_index_time(
        [contract["load_profile"] for contract in local_contracts],
        [contract["time"] for contract in local_contracts]
    )
    # Remote consumption
    x_consumption_remote, y_consumption_remote = change_index_time(
        [contract["load_profile"] for contract in remote_contracts],
        [contract["time"] for contract in remote_contracts]
    )
    # Production
    x_production, y_production = add_productions(producer_profiles)
    # If any of the lists is empty, give at least one point
    if x_consumption_local == [] and y_consumption_local == []:
        x_consumption = [0]
        y_consumption = [0]
    if x_production == [] and y_production == []:
        x_production = [0]
        y_production = [0]
    return [x_consumption_local, y_consumption_local, x_consumption_remote, y_consumption_remote, x_production,
            y_production]
  
