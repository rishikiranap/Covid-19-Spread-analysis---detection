import math
import helper
import sim_parameters
import pandas as pd
import numpy as np
import datetime

transition_probs = sim_parameters.TRASITION_PROBS
holding_times = sim_parameters.HOLDING_TIMES

#Sample creation for the countries and sample ratio provided and return dataframe containing the sample data
def create_sample_data(countries_csv_name, countries, sample_ratio):
    
    #Reading the countries csv file
    data = pd.read_csv(countries_csv_name)
    pd.options.mode.chained_assignment = None
    sample = data[data["country"].isin(countries)]

    #dividing the population of a country to the sample ratio to get the sample size
    sample['population'] = round(sample['population'] // sample_ratio)
    age_groups = ["less_5", "5_to_14", "15_to_24", "25_to_64", "over_65"]
    
    sample_data = []
   
    #For every age group in a country multiply the sample size with the percentage and divide by 100
    for _, row in sample.iterrows():
        
        for age_group in age_groups:
            age_percentage = row[age_group]
            sample_size = int((age_percentage * row['population']) // 100)
            sample_data.extend([{
                "id": i,
                "age_group_name": age_group,
                "country": row["country"]
            } for i in range(len(sample_data), len(sample_data) + sample_size)])
    
    sampledf = pd.DataFrame(sample_data)
    
    return sampledf

def simulate_timeseries(sampledf, start_date, end_date):
    df1 = []
    curr_state = "H"
    for _, row in sampledf.iterrows():
        curr_state = "H"
        start_d = datetime.datetime(*map(int, start_date.split("-")))
        end_d = datetime.datetime(*map(int, end_date.split("-")))
        r = (end_d - start_d).days
        temp = 0
        present_state = "H"
        
        #creating time series DS to store the information for the given time frame
        person_data_list = []
        for _ in range(r + 1):
            temp += 1
            stayd = holding_times[row["age_group_name"]][curr_state]

            person_data = {
                "person_id": row['id'],
                "age_group_name": row["age_group_name"],
                "country": row["country"],
                "date": start_d.strftime("%Y-%m-%d"),
                "state": curr_state,
                "staying_days": stayd,
                "prev_state": present_state,
            }

            person_data_list.append(person_data)

            present_state = curr_state
            #Running the markov chain for simulation
            if stayd == temp or stayd == 0:
                val = transition_probs[row["age_group_name"]][curr_state].values()
                next_state = np.random.choice(
                    list(transition_probs[row["age_group_name"]][curr_state].keys()),
                    p=list(val))
                temp = holding_times[row["age_group_name"]][curr_state]
                present_state = curr_state
                curr_state = next_state
                temp = 0

            start_d += datetime.timedelta(days=1)

        df1.extend(person_data_list)
    #creating the df from the simulated data
    df1 = pd.DataFrame(df1)
    return df1
    
    
#saving the simulated-timeseries to a3-covid-simulated-timeseries.csv
def Saving_timeseries(df1):
    df1.to_csv('a3-covid-simulated-timeseries.csv', index=False)

# Summarizing states for each day of simulation for the provided countries
def generate_summary_data(csv):
    p = csv.groupby(['country', 'date', 'state']).size().reset_index(name='count')
    q = p.pivot(index=['date', 'country'], columns='state', values='count').fillna(0).astype(int)
    #Saving the summarized information to the "a3-covid-summary-timeseries.csv".
    q.to_csv('a3-covid-summary-timeseries.csv')


# The main run function which gets input from the test file
def run(countries_csv_name, countries, start_date, end_date, sample_ratio):
    # Pass the parameters to create sample to the function "create_sample_data" which return the df of sample population.
    sampledf = create_sample_data(countries_csv_name, countries, sample_ratio)
   
    # Pass the sampledf to create a DS to timeseries of the sample from sampledf and run the markov simulation.
    data = simulate_timeseries(sampledf, start_date, end_date)
    
    #calling the saving the timeseries data 
    Saving_timeseries(data)
    
    # Summarizing states for each day of simulation.
    generate_summary_data(data)
    #Calling the create_plot function from the helper function to draw the graphs
    helper.create_plot('a3-covid-summary-timeseries.csv', countries)

