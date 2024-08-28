Below are the required components of your code sample. We will need to see successful demonstration of these data manipulation tasks in whichever programming language you feel best represents your coding ability. We are expecting these to be done in SAS, Stata, Python, or R but if you are planning to use another language, please let us know ASAP. If you have Python knowledge, we strongly recommend submitting in Python.
 
- [x] Reading in data or sets of data in a format other than the programming language’s default file format (e.g., read-in data from Excel or flat text file into Stata)
  - Reads in two .csv files, T_MASTER_CORD.csv and Distance_of_All_Airports_20240308_125630.csv.
- [x] Validating data by performing summaries, frequencies, and/or tabulations 
  - Frequencies for the airports in the distances dataframe, summaries for the end result (full airport distances), and histograms for the distances are printed out.
- [x] Changing the format of data (e.g., converting character date value to the programming language’s date, convert characters/strings to numeric, etc.) 
  - Convert string representing the distance to an integer.
  ```python
  df['DISTANCE'] = df['DISTANCE'].astype(int)
  ```
- [x] Creating and/or calculating new variables from existing variables (e.g., time between two dates) 
  - Calculating a "revised distance" column that is calculated from both the original distance value and a scaled random value. 
    The scaled random value can be a maximum of 30% of the original distance, and a minimum of zero.
  ```python
  df_w_coords['RANDOM_VALUE'] = df_w_coords.apply(lambda row: generate_random_based_on_value(row, 'DISTANCE', 0.3), axis=1).astype(int)
  df_w_coords['REVISED_DISTANCE'] = (df_w_coords['DISTANCE'] + df_w_coords['RANDOM_VALUE']).clip(lower=0).astype(int)
  ```
- [x] Using conditional logic 
  - If statements make sections of code only run if the "goal" output file doesn't exist yet.
- [x] Merging and appending data  
  - Merge airport distance data with individual airport more detailed data.
- [ ] Addressing repetitive processes (e.g., loops) 
- [x] Exporting data to a format other than the programming language’s default file format (e.g., data in Stata exported to Excel, CSV, delimited, etc.) 
  - Results of distances between airports with their latitudes and longitudes inclues are output into two .csv files under the output folder. 

You are welcome to use existing code that was developed for another purpose, as long as it was created by you personally and demonstrates all of the skills listed above. If you need to modify existing code to include additional logic to fit this exercise, that is okay. If you are able to submit a log showing a successful run of the entire code set, that would be ideal but we understand that in some cases, this may not be possible. We will be checking for syntax errors in addition to general demonstration of these data manipulation concepts. It would be ideal for this code sample to be something you have completed as part of your work at RTI but again, we understand that this may not be possible. Please do not send us any accompanying datasets or output that contain project-sensitive information, PHI, PII, etc.
