import pandas as pd


def get_la_data():
    '''
    Returns the Los Angeles Parking Citation Data stored in data/raw
    '''
    df = pd.read_csv('../data/raw/parking-citations.csv')
    return df