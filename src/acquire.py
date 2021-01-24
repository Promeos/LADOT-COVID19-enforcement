import pandas as pd
import os
import time
import json
import requests
import os
from time import sleep
from time import time
from bs4 import BeautifulSoup
from requests import get
from random import randint
from warnings import warn
from IPython.core.display import clear_output


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
    from 2017-2020.
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


###################### REST API Functions ######################
def base_url():
    '''
    Returns base url to acquire LinkedIn job posts.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    string url to acquire LinkedIn data.
    '''
    return  "https://api.twitter.com/2/


def response_endpoint(endpoint):
    '''
    Accepts endpoint from Twitter's API.
    
    Returns 
    Parameters
    ----------
    endpoint : str
        A possible path of "https://api.twitter.com/2/
        
        Example
        -------
        endpoint = "/documentation"
        base_url = "https://api.twitter.com/2/"
        
    Returns
    -------
    requests.models.Response object
    '''
    get_request = requests.get(base_url() + endpoint)
    return get_request


def max_page(url):
    '''
    Accepts a requests.models.Response object
    
    Return the maximum page for a specific endpoint
    Parameters
    ----------
    url : requests.models.Response
        A response from an endpoint using REST API
    
    Returns
    -------
    integer value
    '''
    return url.json()['payload']['max_page']


def page_iterator(data, data_path, stop_page):
    '''
    Accepts an endpoint name, path to endpoint, and number of pages to acquire.
    
    Return a specific H-E-B dataset as a pandas DataFrame.
    Parameters
    ----------
    data : str
        The name of an endpoint to retrieve H-E-B data
    
    data_path : str
        The path to the specified endpoint
    
    stop_page : int
        The page number to stop on - inclusive.
    
    Returns
    -------
    pandas DataFrame
    '''
    df = pd.DataFrame()
    
    for page in range(1, stop_page+1):
        response = requests.get(base_url() + data_path + '?page=' + str(page))
        df = df.append(response.json()['payload'][f'{data}'])

    return df


def check_local_cache(data):
    '''
    Accepts an endpoint from "https://api.twitter.com/2/ and checks to see if a local
    cached version of the data exists
    
    Returns endpoint data as a pandas DataFrame if a local cache exists
    Returns False if a local cache does not exist.
    
    Parameters
    ----------
    data : str
        
    Returns
    -------
    Return cached file as a pandas DataFrame if : os.path.isfile(file_name) == True
    Return False otherwise
    '''
    file_name = f'{data}.csv'
    
    if os.path.isfile(file_name):
        return pd.read_csv(file_name, index_col=False)
    else:
        return False    
    
    
############################# Acquire News Articles ######################################
def check_local_cache(file_name):
    '''
    Accepts a filename and checks to see if a local
    cached version of the data exists
    
    Returns endpoint data as a pandas DataFrame if a local cache exists
    Returns False if a local cache does not exist.
    
    Parameters
    ----------
    file_name : str
        
    Returns
    -------
    Return cached file as a pandas DataFrame if : os.path.isfile(file_name) == True
    Return False otherwise
    '''
    if os.path.isfile(file_name):
        f = open(file_name)
        data = json.load(f)
        return pd.DataFrame(data)
    else:
        return False


def url_request(url):
    '''
    Accepts a URL
    Returns a response object
    '''
    headers = {"User-Agent": "Codeup Data Science"}
    response = get(url, headers=headers)
    return response
    

def web_scrape_in_progress(requests, response, start_time):
    '''
    This function accepts a response object
    Returns the status of url scraped.
    '''
    if response.status_code != 200:
        warn(f"Request{requests}, Status Code {response.status_code}")
    elapsed_time = time() - start_time
    sleep(randint(1, 2))
    requests += 1
    print(f'Request: {requests}; Frequency: {requests/elapsed_time:.2f} requests/s')
    clear_output(wait=True)
    return requests


def get_news_articles():
    '''
    This function returns 3 articles as list of dictionaries.
    
    Each dictionary has a title, date published, and article.
    '''
    file_name = 'news_articles.json'
    # Check to see if a local cache of data exists
    cache = check_local_cache(file_name=file_name)
    
    # If a local cache does not exist, scrape the blog posts
    if cache is False:
        # Create a counter and timer to display update messages throughout the query
        requests = 0
        start_time = time()
        
        # Create an empty list to store each article as a dictionary.
        blog_posts = []
        counter = 0
        # The websites we want to scrape
        blog_urls = [
            'https://www.latimes.com/california/story/2020-03-16/los-angeles-parking-ticket-street-sweeping-coronavirus-covid19',
            'https://www.latimes.com/california/story/2020-10-15/street-sweeping-parking-enforcement-resumes-today',
            'https://abc7.com/society/las-resumed-parking-enforcement-prompts-outcry/7079278/'        
        ]

        for url in blog_urls:
            counter += 1
            
            response = url_request(url=url)
            requests = web_scrape_in_progress(requests=requests, response=response, start_time=start_time)
            soup = BeautifulSoup(response.text, 'html.parser')

            if counter < 3:
                title = soup.find('h1').text.strip()
                date_published = soup.find('div', class_='published-day').text
                article = soup.find('div', class_='rich-text-article-body-content rich-text-body').text.strip()

                blog_posts.append({'date_published': date_published,
                                   'title': title,
                                   'article': article})
            else:
                title = soup.find('h1').get_text()
                date_published = soup.find('meta', attrs={'itemprop': 'uploadDate'})['content']
                article = soup.find('div', class_='body-text').text
 
                blog_posts.append({'date_published': date_published,
                                   'title': title,
                                   'article': article})               

        pd.DataFrame(blog_posts).to_json(file_name)
        return pd.DataFrame(blog_posts)
    else:
        return cache
