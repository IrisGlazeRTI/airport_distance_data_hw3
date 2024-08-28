# Import necessary libraries
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime

# Input data files source: https://www.transtats.bts.gov/Distance.aspx

# Define the function to generate random value based on a column value and multiplier
def generate_random_based_on_value(row, column_name, multiplier):
    return np.random.randint(0, multiplier * row[column_name] + 1)

# Prepare the between airport distances dataframe.
def prepare_distances_data_df(original_input_file_path):
    # Load the CSV data for the distances between airports into a pandas DataFrame.
    df = pd.read_csv(original_input_file_path)
    # Rename some columns.
    df.rename(
        columns={'DISTANCE IN MILES': 'DISTANCE'},
        inplace=True)
    # Exclude rows where the source and destination airports are the same.
    df = df[df['ORIGIN_AIRPORT_SEQ_ID'] != df['DEST_AIRPORT_SEQ_ID']]
    # Convert string representing the distance to an integer.
    df['DISTANCE'] = df['DISTANCE'].astype(int)
    return df

# Prepare the airport facilities dataframe.
def prepare_airport_facilities_df(aviation_facilities_input_file_path):
    # Load the CSV data for individual airport data (which includes latitude and longitude) into a pandas DataFrame.
    airport_facilities_df = pd.read_csv(aviation_facilities_input_file_path)
    # Select a subset of the columns to use.
    airport_facilities_df = airport_facilities_df[
        ['AIRPORT_SEQ_ID', 'AIRPORT_ID', 'LATITUDE', 'LONGITUDE', 'DISPLAY_AIRPORT_CITY_NAME_FULL', 'AIRPORT_STATE_NAME', 'AIRPORT_START_DATE',
         'AIRPORT_COUNTRY_NAME', 'AIRPORT']]
    airport_facilities_df = airport_facilities_df.sort_values(by=['AIRPORT_ID', 'AIRPORT_START_DATE'], ascending=[True, False])
    airport_facilities_df = airport_facilities_df.drop_duplicates(subset='AIRPORT_ID', keep='first')

    return airport_facilities_df

# Print some frequency values and summary statistics.
def validate_data(df):
    # Print summary statistics
    print("Summary Statistics:")
    print(df.describe())

    # Print frequency of unique values in key columns
    print("\nFrequency of unique values in 'ORIGIN_AIRPORT_SEQ_ID':")
    print(df['ORIGIN_AIRPORT_SEQ_ID'].value_counts())

    print("\nFrequency of unique values in 'DEST_AIRPORT_SEQ_ID':")
    print(df['DEST_AIRPORT_SEQ_ID'].value_counts())

# Frequency histogram for specified dataframe and column name.
def plot_histogram(df, column_name):
    plt.figure(figsize=(10, 6))
    plt.hist(df[column_name], bins=30, edgecolor='k', alpha=0.7)
    plt.title(f'Histogram of {column_name}')
    plt.xlabel(column_name)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

# Define a function to log messages
def log_message(message, log_file='process.log'):
    with open(log_file, 'a') as f:
        f.write(f'{datetime.now()}: {message}\n')

# Define the main function
if __name__ == '__main__':

    aviation_facilities_input_file_path = 'T_MASTER_CORD.csv'

    # Specify the path to your CSV file
    original_input_file_path = 'Distance_of_All_Airports_20240308_125630.csv'
    full_revised_file_dir = "output"
    full_revised_file_path = os.path.join(full_revised_file_dir, "full_airport_distances_revised.csv")
    # alternative is REVISED_DISTANCE
    columns_to_export_arr = ['ORIGIN_AIRPORT_SEQ_ID', 'DEST_AIRPORT_SEQ_ID', 'DISTANCE', 'REVISED_DISTANCE', 'LONGITUDE_ORIGIN', 'LATITUDE_ORIGIN', 'LONGITUDE_DEST', 'LATITUDE_DEST', 'DISPLAY_AIRPORT_CITY_NAME_FULL_ORIGIN', 'AIRPORT_COUNTRY_NAME_ORIGIN', 'DISPLAY_AIRPORT_CITY_NAME_FULL_DEST', 'AIRPORT_COUNTRY_NAME_DEST']

    if not os.path.exists(full_revised_file_path):
        df = prepare_distances_data_df(original_input_file_path)
        facilities_df = prepare_airport_facilities_df(aviation_facilities_input_file_path)

        print(len(df))

        # Define a list of column names to rename
        columns_to_rename = ['LATITUDE', 'LONGITUDE', 'DISPLAY_AIRPORT_CITY_NAME_FULL', 'AIRPORT_STATE_NAME', 'AIRPORT_START_DATE', 'AIRPORT_COUNTRY_NAME', 'AIRPORT']

        df_w_coords = pd.merge(df, facilities_df, how="inner", left_on="ORIGIN_AIRPORT_SEQ_ID", right_on="AIRPORT_SEQ_ID", suffixes=(None, "_ORIGIN"))
        # Use a loop to rename columns by appending '_ORIGIN'
        for column in columns_to_rename:
            df_w_coords.rename(columns={column: f'{column}_ORIGIN'}, inplace=True)
        df_w_coords = pd.merge(df_w_coords, facilities_df, how="inner", left_on="DEST_AIRPORT_SEQ_ID", right_on="AIRPORT_SEQ_ID", suffixes=(None, '_DEST'))
        # Use a loop to rename columns by appending '_DEST'
        for column in columns_to_rename:
            df_w_coords.rename(columns={column: f'{column}_DEST'}, inplace=True)

        # Validate data
        validate_data(df_w_coords)

        # Plot histogram of the 'DISTANCE' column
        plot_histogram(df_w_coords, 'DISTANCE')

        df_w_coords['RANDOM_VALUE'] = df_w_coords.apply(lambda row: generate_random_based_on_value(row, 'DISTANCE', 0.3), axis=1).astype(int)
        df_w_coords['REVISED_DISTANCE'] = (df_w_coords['DISTANCE'] + df_w_coords['RANDOM_VALUE']).clip(lower=0).astype(int)

        # Plot histogram of the 'REVISED_DISTANCE' column
        plot_histogram(df_w_coords, 'REVISED_DISTANCE')

        # Select columns to keep for full results dataframe.
        df_w_coords = df_w_coords[columns_to_export_arr]

        print("Printing first 15 rows...")
        print(df_w_coords.head(15))

        # Export the DataFrame to a CSV file
        os.makedirs(full_revised_file_dir, exist_ok=True)

        df_w_coords.to_csv(full_revised_file_path, index=False)  # Set index=False if you don't want to include the index in the CSV
        # If you're running this in a Jupyter notebook or similar environment and want confirmation, you can print a message
        print(f'DataFrame exported to {full_revised_file_path}')
        log_message(f'DataFrame exported to {full_revised_file_path}')
    else:
        # The file exists
        print(f'File already exists: {full_revised_file_path}')
        log_message(f'File {full_revised_file_path} already exists. Delete file and rerun code to recreate.')

    # Takes a random subset sample while maintaining the integrity of the graph structure.
    # Essentially, this means taking a subset of the airports, but keeping all distances associated with the airports sample.
    subset_airport_distance_file_path = os.path.join(full_revised_file_dir, "subset_airport_distances_revised.csv")
    if os.path.exists(full_revised_file_path) and not os.path.exists(subset_airport_distance_file_path):
        full_df = pd.read_csv(full_revised_file_path)
        unique_values = pd.concat([full_df['ORIGIN_AIRPORT_SEQ_ID'], full_df['DEST_AIRPORT_SEQ_ID']]).unique()
        sample_size_max = 40
        valid_sample_values = {}
        if len(unique_values) >= sample_size_max:
            random_sample = np.random.choice(unique_values, size=sample_size_max, replace=False)
            random_sample_set = set(random_sample)
            valid_sample_values = random_sample_set
        else:
            valid_sample_values = set(unique_values)
        filtered_df = full_df[full_df['ORIGIN_AIRPORT_SEQ_ID'].isin(valid_sample_values) & full_df['DEST_AIRPORT_SEQ_ID'].isin(valid_sample_values)]
        filtered_df = filtered_df[columns_to_export_arr]
        print("Printing # of unique origin airport seq. ids in subset distance results.")
        print(len(filtered_df['ORIGIN_AIRPORT_SEQ_ID'].unique()))
        print("Printing # of destination origin airport seq. ids in subset distance results.")
        print(len(filtered_df['DEST_AIRPORT_SEQ_ID'].unique()))
        os.makedirs(full_revised_file_dir, exist_ok=True)
        filtered_df.to_csv(subset_airport_distance_file_path, index=False)  # Set index=False if you don't want to include the index in the CSV
        log_message(f'DataFrame exported to {subset_airport_distance_file_path}')
    else:
        # The file exists
        print(f'File already exists: {subset_airport_distance_file_path}')
        log_message(f'File {subset_airport_distance_file_path} already exists. Delete file and rerun code to recreate.')