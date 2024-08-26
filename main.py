import os
import numpy as np
import pandas as pd


# Function to generate a random number based on another value
def generate_random_based_on_value(row, multiplier=0.3):
    return np.random.randint(0, multiplier * row['DISTANCE'] + 1)


def load_and_prepare_data(original_input_file_path, aviation_facilities_input_file_path):
    # Load the CSV data into DataFrames
    df = pd.read_csv(original_input_file_path)
    facilities_df = pd.read_csv(aviation_facilities_input_file_path)

    # Select relevant columns from facilities_df
    facilities_df = facilities_df[
        ['AIRPORT_SEQ_ID', 'LATITUDE', 'LONGITUDE', 'DISPLAY_AIRPORT_CITY_NAME_FULL', 'AIRPORT_STATE_NAME',
         'AIRPORT_COUNTRY_NAME', 'AIRPORT']]

    # Rename columns in df
    df.rename(columns={'DISTANCE IN MILES': 'DISTANCE'}, inplace=True)
    df = df[df['ORIGIN_AIRPORT_SEQ_ID'] != df['DEST_AIRPORT_SEQ_ID']]
    df['DISTANCE'] = df['DISTANCE'].astype(int)

    return df, facilities_df


def merge_with_facilities(df, facilities_df):
    df_w_coords = pd.merge(df, facilities_df, how="inner", left_on="ORIGIN_AIRPORT_SEQ_ID", right_on="AIRPORT_SEQ_ID")
    df_w_coords.rename(columns={
        'LATITUDE': 'LATITUDE_ORIGIN',
        'LONGITUDE': 'LONGITUDE_ORIGIN',
        'DISPLAY_AIRPORT_CITY_NAME_FULL': 'DISPLAY_AIRPORT_CITY_NAME_FULL_ORIGIN',
        'AIRPORT_COUNTRY_NAME': 'AIRPORT_COUNTRY_NAME_ORIGIN'}, inplace=True)

    df_w_coords = pd.merge(df_w_coords, facilities_df, how="inner", left_on="DEST_AIRPORT_SEQ_ID",
                           right_on="AIRPORT_SEQ_ID")
    df_w_coords.rename(columns={
        'LATITUDE': 'LATITUDE_DEST',
        'LONGITUDE': 'LONGITUDE_DEST',
        'DISPLAY_AIRPORT_CITY_NAME_FULL': 'DISPLAY_AIRPORT_CITY_NAME_FULL_DEST',
        'AIRPORT_COUNTRY_NAME': 'AIRPORT_COUNTRY_NAME_DEST'}, inplace=True)

    return df_w_coords


def process_distances(df):
    df['RANDOM_VALUE'] = df.apply(generate_random_based_on_value, axis=1).astype(int)
    df['REVISED_DISTANCE'] = (df['DISTANCE'] + df['RANDOM_VALUE']).clip(lower=0).astype(int)
    return df


def export_dataframe(df, output_file_path, columns_to_export):
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    df[columns_to_export].to_csv(output_file_path, index=False)
    print(f'DataFrame exported to {output_file_path}')


def generate_subset(full_df, output_file_path, columns_to_export, sample_size=40):
    unique_values = pd.concat([full_df['ORIGIN_AIRPORT_SEQ_ID'], full_df['DEST_AIRPORT_SEQ_ID']]).unique()

    if len(unique_values) >= sample_size:
        random_sample_set = set(np.random.choice(unique_values, size=sample_size, replace=False))
    else:
        random_sample_set = set(unique_values)

    filtered_df = full_df[
        full_df['ORIGIN_AIRPORT_SEQ_ID'].isin(random_sample_set) & full_df['DEST_AIRPORT_SEQ_ID'].isin(
            random_sample_set)]
    export_dataframe(filtered_df, output_file_path, columns_to_export)


def main():
    original_input_file_path = 'Distance_of_All_Airports_20240308_125630.csv'
    aviation_facilities_input_file_path = 'T_MASTER_CORD.csv'
    full_revised_file_dir = "output"
    full_revised_file_path = os.path.join(full_revised_file_dir, "full_airport_distances_revised.csv")
    subset_airport_distance_file_path = os.path.join(full_revised_file_dir, "subset_airport_distances_revised.csv")
    columns_to_export_arr = [
        'ORIGIN_AIRPORT_SEQ_ID', 'DEST_AIRPORT_SEQ_ID',
        'REVISED_DISTANCE', 'LONGITUDE_ORIGIN', 'LATITUDE_ORIGIN',
        'LONGITUDE_DEST', 'LATITUDE_DEST'
    ]

    if not os.path.exists(full_revised_file_path):
        df, facilities_df = load_and_prepare_data(original_input_file_path, aviation_facilities_input_file_path)
        df = merge_with_facilities(df, facilities_df)
        df = process_distances(df)
        export_dataframe(df, full_revised_file_path, columns_to_export_arr)
    else:
        print(f'File already exists: {full_revised_file_path}')

    if os.path.exists(full_revised_file_path) and not os.path.exists(subset_airport_distance_file_path):
        full_df = pd.read_csv(full_revised_file_path)
        generate_subset(full_df, subset_airport_distance_file_path, columns_to_export_arr)
    else:
        print(f'File already exists: {subset_airport_distance_file_path}')


if __name__ == '__main__':
    main()
