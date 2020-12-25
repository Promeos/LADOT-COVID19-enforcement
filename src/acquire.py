import pandas as pd
import os


def get_la_data():
    '''
    Returns the Los Angeles Parking Citation Data stored in data/raw
    '''
    df = pd.read_csv('parking-citations.csv')
    
    return df


def get_parking_data():
    '''
    Returns a dataframe of parking citations from the City of Los Angeles 2017-2020.
    '''
    filename = 'citation-data.csv'
    
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        df = pd.read_csv('parking-citations.csv')
        df = df.loc[df['Issue Date'] >= '2017-01-01'].copy()
        df.to_csv(filename, index=False)
        
        return df
    
    
def get_sweep_data():
    '''
    Returns a dataframe of Street Sweeping citations from the
    City of Los Angeles 2017-2020.
    '''
    filename = 'street-sweeping-data.csv'
    
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        df = get_parking_data()
        df = df.loc[df['Violation Description'] == 'NO PARK/STREET CLEAN'].copy()
        df.to_csv(filename, index=False)
        
        return df