# Import libraries
import pandas as pd
import numpy as np
import os

# Library to covert coordinates.
from pyproj import Proj, transform

################################ Data Prep Functions #########################################
def pct_nulls_per_column(df):
    '''
    This function accepts a pandas dataframe.
    Returns the percentage of values missing in each column.
    
    Parameters
    ----------
    df : pandas.core.DataFrame
        Any pandas dataframe.
        
    Returns
    -------
    None
        Displays a table of each column name with the percent of nulls in that column.
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


def drop_features(df):
    '''
    This function accepts a dataframe and drops columns missing more than 70% of values. Rows with missing values
    are dropped from the dataset.
    
    Returns a dataframe.
    '''
    # Columns missing more than 70% of values.
    columns_to_drop =['vin',
                      'marked_time',
                      'color_description',
                      'body_style_description',
                      'agency_description',
                      'meter_id',
                      'ticket_number']
    
    # Drop columns
    df.drop(columns=columns_to_drop, inplace=True)
    
    # Drop rows with missing values
    df = df.dropna(axis=0)
    
    # Return dataframe
    return df


def convert_coordinates(df):
    '''
    Accepts a pandas dataframe with lat/long values in NAD1983StatePlaneCaliforniaVFIPS0405 feet projection and
    transforms lat/long values to EPSG:4326 World Geodetic System 1984 - used in GPS [Standard].
    
    Returns transformed latitude and longitude columns.
    
    Requirements
    ------------
    You will need to install `pyproj` to use this function.
    > pip install pyproj
    
    Parameters
    ----------
    df : pandas.core.DataFrame
        Any pandas dataframe with latitude and longitude columns with coordinates measured
        in NAD1983StatePlaneCaliforniaVFIPS0405 feet projection.
        
    Returns
    -------
    df : pandas.core.DataFrame
        Returns a pandas dataframe with latitude and longitude columns with EPSG:4326 values.
    '''
    
    # String to represent NAD1983StatePlaneCaliforniaVFIPS0405
    pm = '+proj=lcc +lat_1=34.03333333333333 +lat_2=35.46666666666667 +lat_0=33.5 +lon_0=-118 +x_0=2000000 ' \
         '+y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'

    # Store lat/long values in variables 
    x_latitude, y_longitude = df['latitude'].values, df['longitude'].values
    
    # Transform points between two coordinate systems defined by the Proj instances p1 and p2.
    # Convert coordinates from US Survey Feet to EPSG:4326
    df['longitude'], df['latitude'] = transform(p1=Proj(pm, preserve_units=True),
                                                p2=Proj("+init=epsg:4326"),
                                                x=x_latitude,
                                                y=y_longitude)
    
    # Round lat/log values to standardize.
    df.latitude = np.round(df.latitude, 4)
    df.longitude = np.round(df.longitude, 4)
    
    # Drop citations missing coordinates.
    df = df.loc[(df.longitude != 99999.0)&(df.latitude != 99999.0)]
    
    # Return the dataframe with the transformed columns.
    return df


def add_features(df):
    '''
    Accepts a dataframe
    Returns a dataframe with new features: day_of_week, issue_year, issue_hour, and issue_minute
    '''
    # Create features using issue_data and issue_time
    df = df.assign(
    day_of_week = df.issue_date.dt.day_name(),
    issue_year = df.issue_date.dt.year,
    issue_hour = df.issue_time.dt.hour,
    issue_minute = df.issue_time.dt.minute,
    issue_time = df.issue_time.dt.time
)
    # Cast new features from float to int.
    df.issue_year = df.issue_year.astype(int)
    df.issue_hour = df.issue_hour.astype(int)
    df.issue_minute = df.issue_minute.astype(int)
    
    # Return data
    return df
    

################################ Main Data Prep #########################################
def prep_sweep_data(df):
    '''
    Accepts a pandas dataframe with lat/long values in NAD1983StatePlaneCaliforniaVFIPS0405 feet projection and
    transforms lat/long values to EPSG:4326 World Geodetic System 1984 - used in GPS [Standard].
    
    Returns transformed latitude and longitude columns.
    
    Requirements
    ------------
    You will need to install `pyproj` to use this function.
    > pip install pyproj
    
    Parameters
    ----------
    df : pandas.core.DataFrame
        Any pandas dataframe with latitude and longitude columns with coordinates measured
        in NAD1983StatePlaneCaliforniaVFIPS0405 feet projection.
        
    Returns
    -------
    df : pandas.core.DataFrame
        Returns a pandas dataframe with latitude and longitude columns with EPSG:4326 values.
    '''
    # Remove spaces and lowercase column names.
    formatted_column_names = [x.replace(' ', '_').lower() for x in df.columns.to_list()]
    df.columns = formatted_column_names
    
    # Cast plate expiration from a float to a datetime data type.
    df.plate_expiry_date = df.plate_expiry_date.fillna(0).astype(np.int)
    df.plate_expiry_date = pd.to_datetime(df.plate_expiry_date, format='%Y%m', errors='coerce')
    
    # Cast issue_date and issue_time from a string to a datetime data type.
    df.issue_date = pd.to_datetime(df.issue_date)
    df.issue_time = pd.to_datetime(df.issue_time, format='%H%M', errors='coerce')
    
    # Convert agency from float to integer
    df.agency = df.agency.astype(np.int)

    # Drop columns, convert coordinates, and add new features
    df = drop_features(df)
    df = convert_coordinates(df)
    df = add_features(df)
    
    # Drop the index and sort by issue_date
    df = df.sort_values(by='issue_date')
    df.reset_index(drop=True, inplace=True)
    
    # Return the prepared dataframe.
    return df