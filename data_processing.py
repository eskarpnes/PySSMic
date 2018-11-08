import pandas as pd
import numpy as np
import pickle
import os.path
from definitions import ROOT_DIR


def open_file(file_name):
    path = os.path.join(ROOT_DIR, "results", file_name)
    print("opening " + path)
    with open(path, 'rb') as f:
        res = pickle.load(f)
        contracts = res[0]
        profiles = res[1]
    return contracts, profiles


def get_contracts(file_name):
    contracts, profiles = open_file(file_name)
    return contracts


def get_profiles(file_name):
    contracts, profiles = open_file(file_name)
    return profiles


def rename_columns(contract):
    old_keys = ["id", "time", "time_of_agreement", "load_profile", "job_id", "producer_id"]
    new_keys = ['Contract ID', 'Contract start time', 'Contract agreement time', 'Energy used (Wh)', 'Consumer ID',
                'Producer ID']
    for i in range(0, len(old_keys)):
        contract[new_keys[i]] = contract.pop(old_keys[i])
    return contract


def neighbourhood_to_household(contracts_input, profiles_input, grid_id='grid'):
    household_dict_list = []
    for contracts in contracts_input:
        df = pd.DataFrame(contracts)
        producers = list(df.producer_id.unique())
        producers.remove(grid_id)
        consumers = list(df.job_id.unique())
        all_devices = producers + consumers

        household_dict = dict()
        for device in all_devices:
            before = device.index('[') + 1
            after = device.index(']')
            household_id = device[before:after]
            if household_id in household_dict:
                household_dict[household_id].append(device)
            else:
                household_dict[household_id] = [device]

        household_dict_list.append(household_dict)

    return household_dict_list


# household_dictionary = neigbourhood_to_household(contracts, profiles)


def rewrite_profiles(contracts, profiles):
    profiles_list = []
    for i in range(len(contracts)):
        profiles_run = []
        df = pd.DataFrame(contracts[i])
        producers = df['producer_id'].tolist()
        for producer in producers:
            if producer != 'grid':
                profiles_run.append(profiles[i][producer])
        profiles_list.append(profiles_run)
    return contracts, profiles_list


def average_list_with_lists(list_of_listwithlists):
    list_of_lists = []
    transposed_list_of_listwithlists = map(list, zip(*list_of_listwithlists))
    # print(transposed_list_of_listwithlists)
    for tl in transposed_list_of_listwithlists:
        transposed_tl = map(list, zip(*tl))
        temp_list = []
        for tll in transposed_tl:
            temp_list.append(np.mean(tll))
        list_of_lists.append(temp_list)
    return list_of_lists


# Average value for the values in a dict
def average_from_dict(list_of_dicts):
    new_dict = dict()
    for d in list_of_dicts:
        for key, value in d.items():
            if key in new_dict:
                new_dict[key].append(value)
            else:
                new_dict[key] = [value]

    final_dict = dict()
    for key in new_dict.keys():
        value_list = new_dict[key]
        value_list_transposed = map(list, zip(*value_list))
        new_value_list = []
        for vlt in value_list_transposed:
            new_value_list.append(np.mean(vlt))
        final_dict[key] = new_value_list

    return final_dict


# Pie chart
def remote_versus_local(contracts, grid_id='grid'):
    # Load the contracts into a pandas dataframe
    df = pd.DataFrame.from_dict(contracts)

    # Add a column 'energy_used' for the total energy exchanged during
    # the contract (last value in load_profile)
    load_profiles = df['load_profile'].tolist()
    energy_used = []
    for load_profile in load_profiles:
        energy_used.append(load_profile.iloc[len(load_profile.index) - 1])
    df['energy_used'] = energy_used

    # Get all unique consumer_ids
    consumer_ids = df['job_id'].tolist()
    unique_consumer_ids = list(set(consumer_ids))

    # Determine the local and remote energy used
    output_dict = dict()
    for consumer in unique_consumer_ids:
        # Find all contracts from a specific consumer
        df_consumer_contracts = df.loc[df['job_id'] == consumer]
        # Find all local contracts and sum over the energy
        df_consumer_local = df_consumer_contracts.loc[df_consumer_contracts['producer_id'] != grid_id]
        local_energy = df_consumer_local['energy_used'].sum()
        # Find all remote contracts and sum over the energy
        df_consumer_remote = df_consumer_contracts.loc[df_consumer_contracts['producer_id'] == grid_id]
        remote_energy = df_consumer_remote['energy_used'].sum()
        # Write the consumer_id to a dictionary with a list of his local and remote energy
        output_dict[consumer] = [local_energy, remote_energy]

    return output_dict


# Divides time index by 60 (NOT NOW!) and gives opportunity to accumulate values
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

    x_energy = energy_series.index.tolist()
    y_energy = energy_series.values.tolist()

    return [x_energy, y_energy]


# Line chart: energy produced over time
def add_productions(producer_profiles):
    produced_series = producer_profiles.pop(-1)

    for profile in producer_profiles:
        produced_series += profile

    end_time = int(produced_series.index[-1])
    new_indexes = range(0, end_time+60, 60)
    produced_series = produced_series.reindex(new_indexes)
    produced_series = produced_series.interpolate(method="linear")
    produced_series = produced_series.diff()

    x_production = produced_series.index.tolist()
    y_production = produced_series.values.tolist()

    return x_production, y_production


def energy_over_time(contracts, producer_profiles):
    # Load the contracts into a dataframe
    # CONSUMPTION
    x_consumption, y_consumption = change_index_time(
        [contract["load_profile"] for contract in contracts if contract["producer_id"] is not "grid"],
        [contract["time"] for contract in contracts if contract["producer_id"] is not "grid"]
    )
    # PRODUCTION
    x_production, y_production = add_productions(producer_profiles)

    # If any of the lists is empty, give at least one point
    if x_consumption == [] and y_consumption == []:
        x_consumption = [0]
        y_consumption = [0]
    if x_production == [] and y_production == []:
        x_production = [0]
        y_production = [0]

    return [x_consumption, y_consumption, x_production, y_production]


def peak_to_average_ratio(contracts, producer_profiles, interval=900):
    # Load the contracts into a dataframe
    df = pd.DataFrame.from_dict(contracts)

    # Change the seconds into minutes (round downwards)
    agreement_times = df['time_of_agreement'].tolist()
    agreement_minutes = []
    for at in agreement_times:
        agreement_minutes.append(int(at / 60))
    df['time_of_agreement_minutes'] = agreement_minutes

    # Get consumptions per minute
    x_consumption, y_consumption = change_index_time(df['load_profile'].tolist(), agreement_minutes, False)

    # Determine the consumption per quarter (by summing up all consumptions per minute)
    consumption_per_quarter = []
    quarter_consumption = 0.0
    for i in range(len(x_consumption)):
        quarter_consumption += y_consumption[i]
        if x_consumption[i] % interval == 0:
            consumption_per_quarter.append(quarter_consumption)
            quarter_consumption = 0

    # Determine average and peak consumption
    average_consumption = np.mean(consumption_per_quarter)
    max_consumption = max(consumption_per_quarter)

    return max_consumption / average_consumption


def neighbourhood_execution_remote_versus_local(contracts_input, profiles_input):
    contracts_input, profiles_input = rewrite_profiles(contracts_input, profiles_input)
    output = []
    for i in range(len(contracts_input)):
        output.append(remote_versus_local(contracts_input[i]))
    output_combined = average_from_dict(output)
    return [output, output_combined]


def neighbourhood_execution_energy_over_time_average(contracts_input, profiles_input):
    contracts_input, profiles_input = rewrite_profiles(contracts_input, profiles_input)
    output = []
    for i in range(len(contracts_input)):
        output.append(energy_over_time(contracts_input[i], profiles_input[i]))
        break
    output_combined = average_list_with_lists(output)
    return [output, output_combined]


def neighbourhood_execution_energy_over_time(contracts_input, profiles_input):
    return energy_over_time(contracts_input, list(profiles_input.values()))


def neighbourhood_execution_peak_to_average(contracts_input, profiles_input):
    contracts_input, profiles_input = rewrite_profiles(contracts_input, profiles_input)
    output = []
    for i in range(len(contracts_input)):
        output.append(peak_to_average_ratio(contracts_input[i], profiles_input[i]))
    output_combined = np.mean(output)
    return [output, output_combined]


def household_execution_local_versus_remote(contracts_input, households, profiles_input):
    output = []
    households_list = []
    for i in range(len(contracts_input)):
        household_ids = households[i].keys()
        households_list.append(list(household_ids))
        output_household = []
        for household in household_ids:
            household_devices = households[i][household]
            contracts_household = []
            for j in range(len(contracts_input[i])):
                if contracts_input[i][j]['job_id'] in household_devices:
                    contracts_household.append(contracts_input[i][j])
            output_household.append(remote_versus_local(contracts_household))
        output.append(output_household)
    return output, households_list


def household_execution_energy_over_time(contracts_input, profiles_input, households):
    output = []
    households_list = []
    for i in range(len(contracts_input)):
        household_ids = households[i].keys()
        households_list.append(list(household_ids))
        output_household = []
        for household in household_ids:
            household_devices = households[i][household]
            contracts_household = []
            for j in range(len(contracts_input[i])):
                if contracts_input[i][j]['job_id'] in household_devices or contracts_input[i][j]['producer_id'] \
                        in household_devices:
                    contracts_household.append(contracts_input[i][j])
            profile_keys = profiles_input[i].keys()
            profiles_household = []
            for key in profile_keys:
                if key in household_devices:
                    profiles_household.append(profiles_input[i][key])
            output_household.append(energy_over_time(contracts_household, profiles_household))
        output.append(output_household)
    return output, households_list


def household_execution_peak_to_average_ratio(contracts_input, profiles_input, households):
    output = []
    households_list = []
    for i in range(len(contracts_input)):
        household_ids = households[i].keys()
        households_list.append(list(household_ids))
        output_household = []
        for household in household_ids:
            household_devices = households[i][household]
            contracts_household = []
            for j in range(len(contracts_input[i])):
                if contracts_input[i][j]['job_id'] in household_devices or contracts_input[i][j]['producer_id'] \
                        in household_devices:
                    contracts_household.append(contracts_input[i][j])
            profile_keys = profiles_input[i].keys()
            profiles_household = []
            for key in profile_keys:
                if key in household_devices:
                    profiles_household.append(profiles_input[i][key])
            output_household.append(peak_to_average_ratio(contracts_household, profiles_household))
        output.append(output_household)
    return output, households_list
