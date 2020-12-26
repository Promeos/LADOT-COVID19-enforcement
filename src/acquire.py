import pandas as pd
import os
import time

# Functions to scrape youtube comments.
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#################################### Acquire Parking Citation Data ######################################
def get_citation_data():
    '''
    Returns the Los Angeles Parking Citation Data as a pandas dataframe.
    
    Prerequisite:
    - Download dataset from https://www.kaggle.com/cityofLA/los-angeles-parking-citations
    
    df : pandas.core.DataFrame
        Pandas dataframe of parking citations from Los Angeles.
    '''
    df = pd.read_csv('parking-citations.csv')
    return df


def get_sweep_data():
    '''
    Returns a dataframe of Street Sweeping citations issued in Los Angeles, CA
    from 2017-Today.
    '''
    # File name of street sweeping data
    filename = 'street-sweeping-data.csv'

    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        df = get_citation_data()
        
        # Filter for street sweeper citations data issued 2017-Today.
        df_sweep = df.loc[(df['Issue Date'] >= '2017-01-01')&(df['Violation Description']=='NO PARK/STREET CLEAN')]
        
        # Cache the filtered dataset
        df_sweep.reset_index(drop=True, inplace=True)
        df_sweep.to_csv(filename, index=False)
        return df_sweep


#################################### Acquire Social Media Data ######################################
def  get_yt_data():
    '''
    This function scrapes comments from a youtube video and
    Returns a dataframe of comments.
    
    https://www.youtube.com/watch?v=arNAJ4DgGMk
    '''
    filename = 'youtube_comments.csv'
    
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        # Create an empty list to store comments
        data=[]

        # Create a loop to scrape youtube comments every 15 seconds.
        with Chrome() as driver:
            wait = WebDriverWait(driver,15)
            driver.get("https://www.youtube.com/watch?v=arNAJ4DgGMk")

            for item in range(10): 
                wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
                time.sleep(15)

            for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content"))):
                data.append(comment.text)
    
    # Remove about section from the webpage and normalize text
    df = pd.DataFrame(data[2:], columns=['comments'])
    df = df.comments.str.lower().str.replace(r'\W+', ' ').str.strip()
    df.to_csv(filename, index=False)
    
    return df


def  get_twitter_data():
    '''
    
    '''
    pass