# Write supporting functions here
import pandas as pd
import numpy as np
import folium
from pyproj import Proj, transform


def pct_missing_values_per_column(df):
    '''
    Accepts a dataframe and returns the percentage of values missing in each column.
    '''
    # Total the null values in each column
    nulls = df.isnull().sum()
    
    # Store the length of the dataframe: Number of rows
    data_length = df.shape[0]

    # Divide the number of missing values by the length of the dataframe
    pct_missing = (nulls/data_length).sort_values(ascending=False)
    
    # Apply formatting for presentation.
    pct_missing_chart = pct_missing.apply("{0:.2%}".format)

    # Display the results.
    print('Percentage of values missing per column')
    print('-' * 39)
    print(f"{pct_missing_chart}")


def prep_la_data(df):
    '''
    This function accepts the Los Angeles Parking Citation dataset and returns a dataframe ready
    for exploration.
    '''
    # Remove spaces and lowercase column names.
    formatted_column_names = [x.replace(' ', '_').lower() for x in df.columns.to_list()]
    df.columns = formatted_column_names
    
    # Cast plate expiration from a float to a datetime data type.
    df.plate_expiry_date = df.plate_expiry_date.fillna(0).astype(np.int)
    df.plate_expiry_date = pd.to_datetime(df.plate_expiry_date, format='%Y%m', errors='coerce')
    
    # Cast issue date from a string to a datetime data type.
    df.issue_date = pd.to_datetime(df.issue_date)
    df['day_of_week'] = df.issue_date.dt.day_name()
    df['issue_year'] = df.issue_date.dt.year
    df['issue_time'] = pd.to_datetime(df.issue_time,
                                      format='%H%M',
                                      errors='coerce')

    df['issue_hour'] = df.issue_time.dt.hour
    df['issue_minute'] = df.issue_time.dt.minute
    df.issue_time = df.issue_time.dt.time
    
    
    
    # Remove columns missing a majority of values.
    columns_to_drop =['vin',
                      'marked_time',
                      'color_description',
                      'body_style_description',
                      'agency_description',
                      'meter_id',
                      'ticket_number']
    
    # Drop values.
    df.drop(columns=columns_to_drop, inplace=True)
    df = df.dropna(axis=0)
    
    # Cast agency column from float as integer datatype.
    # Cast columns extracted from issue date as integers.
    df.agency = df.agency.astype(np.int)
    df.issue_year = df.issue_year.astype(int)
    df.issue_hour = df.issue_hour.astype(int)
    df.issue_minute = df.issue_minute.astype(int)
    
    # Drop rows missing a coordinate information 
    df = df.loc[(df.longitude != 99999.0)&(df.latitude != 99999.0)]
    
    # Set the index to issue_date and sort in ascending order
    df.reset_index(drop=True, inplace=True)
    
    # Return the prepared dataframe.
    return df


def convert_coordinates(df):
    '''
    
    '''
    pm = '+proj=lcc +lat_1=34.03333333333333 +lat_2=35.46666666666667 +lat_0=33.5 +lon_0=-118 +x_0=2000000 ' \
         '+y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'


    x_coord, y_coord = df['latitude'].values, df['longitude'].values

    df['longitude'], df['latitude'] = transform(Proj(pm, preserve_units = True),
                                                Proj("+init=epsg:4326")
                                                ,x_coord
                                                ,y_coord)
    df.latitude = np.round(df.latitude, 4)
    df.longitude = np.round(df.longitude, 4)
    
    return df