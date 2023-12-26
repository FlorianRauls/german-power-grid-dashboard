import pandas as pd
import os
import sqlite3
import zipfile
import pandas as pd
import os


# read data from sqlite database
with zipfile.ZipFile(os.path.join('data', 'time_series.zip'), 'r') as zip_ref:
    zip_ref.extractall('data')
db_file_path = os.path.join('data', 'time_series.sqlite')
conn = sqlite3.connect(db_file_path)
data = pd.read_sql_query("SELECT * FROM time_series_15min_singleindex", conn)
conn.close()

# Convert timestamps to datetime objects
data['utc_timestamp'] = pd.to_datetime(data['utc_timestamp'])
data['cet_cest_timestamp'] = pd.to_datetime(data['cet_cest_timestamp'])

# Filter columns related to Germany (DE)
de_columns = [col for col in data.columns if 'DE_' in col]
de_columns.extend(['utc_timestamp', 'cet_cest_timestamp'])
df_de = data[de_columns]

# Fill missing values with rolling mean
df_de.drop(['utc_timestamp', 'cet_cest_timestamp'], axis=1).fillna(df_de.drop(['utc_timestamp', 'cet_cest_timestamp'], axis=1).rolling(100, min_periods=1).mean(), inplace=True)

# Feature Engineering
# Extracting time-based features
df_de['hour'] = df_de['utc_timestamp'].dt.hour
df_de['day'] = df_de['utc_timestamp'].dt.day
df_de['month'] = df_de['utc_timestamp'].dt.month
df_de['year'] = df_de['utc_timestamp'].dt.year

# Creating lag features (example: 1-hour lag)
# Adjust the number 4 to the appropriate lag period for your analysis
df_de['lag_1_hour'] = df_de['DE_load_actual_entsoe_transparency'].shift(4)

# Rolling window statistics
df_de['rolling_24_hour_mean'] = df_de['DE_load_actual_entsoe_transparency'].rolling(window=96).mean()

# Dropping the original timestamp columns as they are no longer needed
df_de.drop(['utc_timestamp', 'cet_cest_timestamp'], axis=1, inplace=True)

# save a sample of the cleaned data as a csv file
sample_csv_file_path = os.path.join('data', 'sample_output.csv')
df_de.sample(50).to_csv(sample_csv_file_path, index=False)

# save the cleaned data to a sqlite database
cleaned_db_file_path = os.path.join('data', 'cleaned_data.sqlite')
conn = sqlite3.connect(cleaned_db_file_path)
df_de.to_sql('cleaned_data', conn, if_exists='replace', index=False)
conn.close()
