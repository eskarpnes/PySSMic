import pandas as pd

# def load_profile_from_csv(csv):
#     split_by_new_line = filter(lambda x: len(x) > 2, csv.split("\n"))
#     parsed = [[float(cell) for cell in line.split(" ")] for line in split_by_new_line]
#     timestamps = map(lambda x: x[0], parsed)
#     values = map(lambda x: x[1], parsed)
#     return pd.Series(data=values, index=timestamps)

#load_profile_csv = open('91.csv', "r").read()
#lp1 = load_profile_from_csv(load_profile_csv)

#example_contracts = [{'contract_id':100, 'time':'16:23', 'time_of_agreement': 20, 'load_profile':lp1, 'consumer_id':10, 'producer_id':1}, {'contract_id':2, 'time':'17:24', 'time_of_agreement': 500, 'load_profile':lp2, 'consumer_id':1, 'producer_id':2}, {'contract_id':3, 'time':'16:53', 'time_of_agreement': 300, 'load_profile':lp3, 'consumer_id':2, 'producer_id':1}, {'contract_id':4, 'time':'17:21', 'time_of_agreement': 300, 'load_profile':lp4, 'consumer_id':1, 'producer_id':1}, {'contract_id':8, 'time':'16:39', 'time_of_agreement': 600, 'load_profile':lp5, 'consumer_id':2, 'producer_id':2}]


#PIE CHART: REMOTE VERSUS LOCAL
def remote_versus_local(contracts, grid_id):
    # Load the contracts into a pandas dataframe
    df = pd.DataFrame.from_dict(contracts)

    #Add a column 'energy_used' for the total energy exchanged during
    # the contract (last value in load_profile)
    load_profiles = df['load_profile'].tolist()
    energy_used = []
    for load_profile in load_profiles:
        energy_used.append(load_profile.iloc[len(load_profile.index)-1])
    df['energy_used'] = energy_used

    # Get all unique consumer_ids
    consumer_ids = df['consumer_id'].tolist()
    unique_consumer_ids = list(set(consumer_ids))

    # Determine the local and remote energy used
    output_dict = dict()
    for consumer in unique_consumer_ids:
        # Find all contracts from a specific consumer
        df_consumer_contracts = df.loc[df['consumer_id'] == consumer]
        # Find all local contracts and sum over the energy
        df_consumer_local = df_consumer_contracts.loc[df_consumer_contracts['producer_id'] != grid_id]
        local_energy = df_consumer_local['energy_used'].sum()
        #Find all remote contracts and sum over the energy
        df_consumer_remote = df_consumer_contracts.loc[df_consumer_contracts['producer_id'] == grid_id]
        remote_energy = df_consumer_remote['energy_used'].sum()
        # Write the consumer_id to a dictionary with a list of his local and remote energy
        output_dict[consumer] = [local_energy, remote_energy]

    return output_dict


#OUTPUT TABLE
def contract_table(contracts):
    #Write the contracts to a pandas dataframe
    df = pd.DataFrame.from_dict(contracts)
    #Drop the columns load_profile and time as they are not used
    df = df.drop(['load_profile', 'time'], axis=1)
    # Reorder the columns in the prefered order
    df = df[['contract_id', 'time_of_agreement', 'consumer_id','producer_id']]
    return df