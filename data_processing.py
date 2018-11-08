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
    print("CONTRACTS")
    print(len(contracts))
    print(len(contracts[0]))
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

######### profiles to list ########
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
###################################

####### IDENTIFY HOUSEHOLD ########
def neigbourhood_to_household(contracts_input, profiles_input, grid_id='grid'):
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

household_dictionary = neigbourhood_to_household(contracts, profiles)

###################################

######## HANDLING AVERAGES ########
# Average values in a list with lists
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

###################################

###### PREPROCESS INPUT DATA ######
# Changes the time according to the starting time and interpolates
def change_index_time(df_energy_list, start_times=[]):
    i = 0
    df_energy_output = pd.Series()
    for df_energy_input in df_energy_list:
        # Adjust the index based upon start time (only when start time is not zero)
        if start_times != []:
            index_list = df_energy_input.index.tolist()
            index_start = [x + start_times[i] for x in index_list]
            i += 1
            df_energy_input.index = index_start

        # Insert an index for every second
        all_indices = list(range(int(df_energy_input.index[-1]) + 1))
        df_energy_all = df_energy_input.reindex(all_indices)
        # Fill al NaN values by interpolating
        df_energy_all = df_energy_all.interpolate()
        # Remaining ones are before the first start value fill those with 0
        df_energy_all = df_energy_all.fillna(0)
        # Remove the cumulative part
        df_energy_all = df_energy_all.diff()
        # Remaining ones are before the first start value fill those with 0
        df_energy_all = df_energy_all.fillna(0)
        # Save the results to one list
        if df_energy_output.empty == True:
            df_energy_output = df_energy_all
        else:
            df_energy_output = df_energy_output.combine(df_energy_all, lambda a1, a2: a1 + a2, fill_value=0)

    x_energy = df_energy_output.index.tolist()
    y_energy = df_energy_output.values.tolist()

    return [x_energy, y_energy]

# Pie chart: remote versus local
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

# Line chart: energy over time
def energy_over_time(contracts, producer_profiles):
    # Load the contracts into a dataframe
    df = pd.DataFrame.from_dict(contracts)

    # CONSUMPTION
    x_consumption, y_consumption = change_index_time(df['load_profile'].tolist(), df['time_of_agreement'].tolist())

    # PRODUCTION
    x_production, y_production = change_index_time(producer_profiles)

    # If any of the lists is empty, give at least one point
    if x_consumption == [] and y_consumption == []:
        x_consumption = [0]
        y_consumption = [0]
    if x_production == [] and y_production == []:
        x_production = [0]
        y_production = [0]

    return [x_consumption, y_consumption, x_production, y_production]

# Peak to average ratio
def peak_to_average_ratio(x_consumption, y_consumption, interval=900):
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

###################################


############ OUTPUT ###############

# Remote verus local
def neighbourhood_execution_remote_versus_local(contracts_input, profiles_input):
    contracts_input, profiles_input = rewrite_profiles(contracts_input, profiles_input)
    output = []
    for i in range(len(contracts_input)):
        output.append(remote_versus_local(contracts_input[i]))
    output_combined = average_from_dict(output)
    return [output, output_combined]

def household_execution_remote_versus_local(output_neighbourhood, household_dictionary):
    output_list = []
    household_list = []
    for run in range(len(output_neighbourhood)):
        run_list = []
        houses_run = []
        for household in household_dictionary[run]:
            houses_run.append(household)
            household_devices = household_dictionary[run][household]
            household_dict = dict()
            for device in household_devices:
                if device in output_neighbourhood[run]:
                    household_dict[device] = output_neighbourhood[run][device]
            run_list.append(household_dict)
        output_list.append(run_list)
        household_list.append(houses_run)
    return [output_list, household_list]

# output, output_combined = neighbourhood_execution_remote_versus_local(contracts,profiles)
# household_execution_remote_versus_local(output, household_dictionary)

# Get output for energy_over_time and peak_to_average
def household_execution(contracts_input, profiles_input, households):
    output_energy_over_time = []
    output_peak_average_ratio = []
    households_list = []

    for run in range(len(contracts_input)):
        household_ids = households[run].keys()
        households_list.append(list(household_ids))
        output_eot = []
        output_par = []
        for household in household_ids:
            household_devices = households[i][household]
            contracts_household = []
            for contract in range(len(contracts_input[run])):
                if contracts_input[run][contract]['job_id'] in household_devices or contracts_input[run][contract][
                    'producer_id'] in household_devices:
                    contracts_household.append(contracts_input[run][contract])
            profile_keys = profiles_input[run].keys()
            profiles_household = []
            for key in profile_keys:
                if key in household_devices:
                    profiles_household.append(profiles_input[run][key])

            energy_output = energy_over_time(contracts_household, profiles_household)
            output_eot.append(energy_output)
            output_par.append(peak_to_average_ratio(energy_output[0], energy_output[1]))
        output_energy_over_time.append(output_eot)
        output_peak_average_ratio.append(output_par)
    return [households_list, output_energy_over_time, output_peak_average_ratio]

household_list, output_energy_over_time, output_peak_average_ratio = household_execution(contracts, profiles,
                                                                                         household_dictionary)

# Energy over time
def household_execution_energy_over_time(output_energy_over_time, household_list):
    return [output_energy_over_time, household_list]

def neighbourhood_execution_energy_over_time(output_energy_over_time):
    for run in range(len(output_energy_over_time)):
        run_results = output_energy_over_time[run]

    return None

# household_execution_energy_over_time(output_energy_over_time, household_list)
# neighbourhood_execution_energy_over_time(output_energy_over_time)

# Peak to average ratio
def household_execution_peak_to_average(output_peak_average_ratio, household_list):
    return [output_peak_average_ratio, household_list]

def neighbourhood_execution_peak_to_average(output_peak_average_ratio):
    return None #return [output, output_combined]

