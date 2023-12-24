import pandas as pd
import os
import sqlite3
import zipfile


# read data from sqlite database
with zipfile.ZipFile(os.path.join('data', 'time_series.zip'), 'r') as zip_ref:
    zip_ref.extractall('data')
db_file_path = os.path.join('data', 'time_series.sqlite')
conn = sqlite3.connect(db_file_path)
data = pd.read_sql_query("SELECT * FROM time_series_30min_singleindex", conn)

# TODO: Clean the data
data_clean = data.copy()

# Saving the cleaned dataset
cleaned_csv_file_path = os.path.join('data', 'cleaned_national_generation_capacity.csv')
data_clean.to_csv(cleaned_csv_file_path, index=False)


