import pandas as pd
import numpy as np
import os

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# https://www.transtats.bts.gov/Distance.aspx

# Function to generate a random number based on another value
def generate_random_based_on_value(row):
    multiplier = 0.3
    return np.random.randint(0, multiplier * row['DISTANCE'] + 1)

if __name__ == '__main__':

    aviation_facilities_input_file_path = 'T_MASTER_CORD.csv'

    # Specify the path to your CSV file
    original_input_file_path = 'Distance_of_All_Airports_20240308_125630.csv'
    full_revised_file_dir = "output"
    full_revised_file_path = full_revised_file_dir + "/full_airport_distances_revised.csv"
    # alternative is REVISED_DISTANCE
    columns_to_export_arr = ['ORIGIN_AIRPORT_SEQ_ID', 'DEST_AIRPORT_SEQ_ID', 'REVISED_DISTANCE', 'LONGITUDE_ORIGIN', 'LATITUDE_ORIGIN', 'LONGITUDE_DEST', 'LATITUDE_DEST']

    if not os.path.exists(full_revised_file_path) or True:
        # Load the CSV data into a pandas DataFrame
        df = pd.read_csv(original_input_file_path)
        facilities_df = pd.read_csv(aviation_facilities_input_file_path)
        facilities_df = facilities_df[['AIRPORT_SEQ_ID', 'LATITUDE', 'LONGITUDE', 'DISPLAY_AIRPORT_CITY_NAME_FULL', 'AIRPORT_STATE_NAME', 'AIRPORT_COUNTRY_NAME', 'AIRPORT']]

        df.rename(
            columns={'DISTANCE IN MILES': 'DISTANCE'},
            inplace=True)
        df = df[df['ORIGIN_AIRPORT_SEQ_ID'] != df['DEST_AIRPORT_SEQ_ID']]
        df['DISTANCE'] = df['DISTANCE'].astype(int)

        # Display the first few rows of the DataFrame to confirm successful loading
        #print(df.head(20))
        print(len(df))

        #print(df.sort_values(by='DISTANCE', ascending=True).head(100))

        unique_values_origin = df['ORIGIN_AIRPORT_SEQ_ID'].unique()
        print(len(unique_values_origin))

        unique_values_dest = df['DEST_AIRPORT_SEQ_ID'].unique()
        print(len(unique_values_dest))

        df_w_coords = pd.merge(df, facilities_df, how="inner", left_on="ORIGIN_AIRPORT_SEQ_ID", right_on="AIRPORT_SEQ_ID", suffixes=(None, "_ORIGIN"))
        df_w_coords.rename(
            columns={'LATITUDE': 'LATITUDE_ORIGIN', 'LONGITUDE': 'LONGITUDE_ORIGIN', 'DISPLAY_AIRPORT_CITY_NAME_FULL': 'DISPLAY_AIRPORT_CITY_NAME_FULL_ORIGIN', 'AIRPORT_COUNTRY_NAME': 'AIRPORT_COUNTRY_NAME_ORIGIN'},
            inplace=True)
        df_w_coords = pd.merge(df_w_coords, facilities_df, how="inner", left_on="DEST_AIRPORT_SEQ_ID", right_on="AIRPORT_SEQ_ID", suffixes=(None, '_DEST'))
        df_w_coords.rename(
            columns={'LATITUDE': 'LATITUDE_DEST', 'LONGITUDE': 'LONGITUDE_DEST', 'DISPLAY_AIRPORT_CITY_NAME_FULL': 'DISPLAY_AIRPORT_CITY_NAME_FULL_DEST', 'AIRPORT_COUNTRY_NAME': 'AIRPORT_COUNTRY_NAME_DEST'},
            inplace=True)

        df = df_w_coords

        # 388384 -> 388380

        df['RANDOM_VALUE'] = df.apply(generate_random_based_on_value, axis=1).astype(int)
        df['REVISED_DISTANCE'] = (df['DISTANCE'] + df['RANDOM_VALUE']).clip(lower=0).astype(int)

        #sorted_df = df.sort_values(by='DISTANCE', ascending=True)

        # Display the sorted DataFrame to confirm ordering
        #print(sorted_df.head(200))

        print(df)

        #print(df.head(100))

        # Export the DataFrame to a CSV file
        os.makedirs(full_revised_file_dir, exist_ok=True)
        df = df[columns_to_export_arr]
        df.to_csv(full_revised_file_path, index=False)  # Set index=False if you don't want to include the index in the CSV
        # If you're running this in a Jupyter notebook or similar environment and want confirmation, you can print a message
        print(f'DataFrame exported to {full_revised_file_path}')
    else:
        # The file exists
        print(f'File already exists: {full_revised_file_path}')

    subset_airport_distance_file_path = full_revised_file_dir + "/subset_airport_distances_revised.csv"
    if os.path.exists(full_revised_file_path) and not os.path.exists(subset_airport_distance_file_path):
        full_df = pd.read_csv(full_revised_file_path)
        unique_values = pd.concat([full_df['ORIGIN_AIRPORT_SEQ_ID'], full_df['DEST_AIRPORT_SEQ_ID']]).unique()
        sample_size = 40
        valid_sample_values = {}
        if len(unique_values) >= sample_size:
            random_sample = np.random.choice(unique_values, size=sample_size, replace=False)
            random_sample_set = set(random_sample)
            valid_sample_values = random_sample_set
        else:
            valid_sample_values = set(unique_values)
        filtered_df = full_df[full_df['ORIGIN_AIRPORT_SEQ_ID'].isin(valid_sample_values) & full_df['DEST_AIRPORT_SEQ_ID'].isin(valid_sample_values)]
        filtered_df = filtered_df[columns_to_export_arr]
        print(len(filtered_df['ORIGIN_AIRPORT_SEQ_ID'].unique()))
        print(len(filtered_df['DEST_AIRPORT_SEQ_ID'].unique()))
        os.makedirs(full_revised_file_dir, exist_ok=True)
        filtered_df.to_csv(subset_airport_distance_file_path, index=False)  # Set index=False if you don't want to include the index in the CSV
    else:
        # The file exists
        print(f'File already exists: {subset_airport_distance_file_path}')