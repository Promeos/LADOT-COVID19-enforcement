import pandas as pd
import os
import sys

import json

import time
from time import time

import tqdm
import requests
from requests import get
from time import sleep

from bs4 import BeautifulSoup
from random import randint
from warnings import warn
from IPython.core.display import clear_output

# Functions to scrape youtube comments
# from selenium.webdriver import Chrome
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(1, '../env.py')
import env


#################################### Acquire Parking Citation Data ######################################
def get_citation_data():
    '''
    Returns the Los Angeles Parking Citation Data as a pandas dataframe.
    
    Prerequisite:
    - Download dataset from https://www.kaggle.com/cityofLA/los-angeles-parking-citations
    
    df : pandas.core.DataFrame
        Pandas dataframe of Los Angeles parking citations.
    '''
    df = pd.read_csv('parking-citations.csv')
    return df


def get_sweep_data():
    '''
    Returns a dataframe of Street Sweeping citations issued in
    Los Angeles, CA from 01/01/2017 - 12/22/2020
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


#################################### Acquire Twitter Data ###################################################
def auth():
    '''
    Bearer Token used to access Twitter's API V2
    
    Returns
    -------
    env.bearer_token : str
        alphanumeric string
    '''
    return env.bearer_token


def create_header():
    '''
    Header required to access Twitter's API V2
    
    Returns
    -------
    headers : dict
        A dictionary to store login credentials. This 
        header is required for all GET requests to Twitter's API.
    '''
    headers = {"Authorization": "Bearer {}".format(auth())}
    return headers


def check_local_cache(file):
    '''
    Accepts a file name and checks to see if a local
    cached version of the data exists.
    
    Parameters
    ----------
    file : str
        The name of the file in the local directory
        
    Returns
    -------
    Return cached file as a pandas DataFrame if : os.path.isfile(file_name) == True
    Return False otherwise
    '''
    if os.path.isfile(file):
        return pd.read_csv(file, index_col=False)
    else:
        return False
    
    
def get_twitter_usernames():
    '''
    A list of dictionaries containing the unique twitter id, name, and username of
    Los Angeles government officials who signed the motion to resume street sweeping
    on 10/15/2020.
    
    Link to document:
    https://github.com/Promeos/LADOT-COVID19-enforcement/blob/main/city-documents/city-council/public-outreach-period.pdf
    
    Note: Mayor Gracetti did not sign the motion.
    
    Returns
    -------
    twitter_accounts : pandas.core.DataFrame
        A dataframe containing the twitter id, name, and username of each government entity.
    '''
    data = [
        {
            "id": "17070113",
            "name": "MayorOfLA",
            "username": "MayorOfLA"
        },
        {
            "id": "61261275",
            "name": "LADOT",
            "username": "LADOTofficial"
        },
        {
            "id": "956763276",
            "name": "Nury Martinez",
            "username": "CD6Nury"
        },
        {
            "id": "893602974",
            "name": "Curren D. Price, Jr.",
            "username": "CurrenDPriceJr"
        },
        {
            "id": "341250146",
            "name": "Joe Buscaino",
            "username": "JoeBuscaino"
        }
    ]
    
    # Gil has not tweeted since 2019.
    # {
    # "id": "1167156666",
    # "name": "Gil Cedillo",
    # "username": "cmgilcedillo"
    # }
    
    # Transform the list of dictionaries into a dataframe
    twitter_accounts = pd.DataFrame.from_records(data)
    
    # Format the names of the Mayor of Los Angeles and LADOT.
    twitter_accounts.name = twitter_accounts.name.str.replace('MayorOfLA', 'Eric Garcetti')
    twitter_accounts.name = twitter_accounts.name.str.replace('LADOT', 'Los Angeles Department of Transportation')
    
    # Return the dataframe of Twitter accounts.
    return twitter_accounts


def tweet_info(account, tweet):
    '''
    
    '''
    tweet_data = pd.DataFrame({'post_time': pd.to_datetime(tweet['created_at']),
                                           'id': account['id'],
                                           'name': account['name'],
                                           'username': account['username'],
                                           'tweet': tweet['text'].lower(),
                                           'retweet_count': tweet['public_metrics']['retweet_count'],
                                           'reply_count': tweet['public_metrics']['reply_count'],
                                           'like_count': tweet['public_metrics']['like_count'],
                                           'quote_count': tweet['public_metrics']['quote_count'],
                                           'tweet_url_id': tweet['id']
                                           },index=[0])
    return tweet_data
    
    
def get_twitter_data():
    '''
    Returns the twitter data for each city council official that signed a memo to resume Street Sweeping on
    10/15/2020.
    
    Link to document:
    https://github.com/Promeos/LADOT-COVID19-enforcement/blob/main/city-documents/city-council/public-outreach-period.pdf

    Note: Mayor Gracetti did not sign the motion.
    
        
    Returns (Conditional)
    -------
    If `cache` is not False:
        cache : pandas.core.frame.DataFrame
            The cached tweets of each city council representative and LADOT between 09/30/2020 - 10/15/2020
            
    If `cache` is False:
        df : pandas.core.frame.DataFrame
             The cached tweets of each city council representative and LADOT between 09/30/2020 - 10/15/2020
    '''
    # Check the local directory for the Twitter data
    filename = 'tweets.csv'
    cache = check_local_cache(file=filename)
    
    
    if cache is False:
        # Store the dict of council members & LADOT's Twitter info.
        twitter_accounts = get_twitter_usernames()
        
        # Calculate the # of Twitter accounts in `twitter_accounts`
        
        num_accounts = len(twitter_accounts)
        
        # Store the URL header to a variable
        credentials = create_header()
        
        # Create an empty DataFrame to store the tweets from each account
        df = pd.DataFrame()

        # For each account in the dataframe `twitter_accounts` acquire all tweets from
        # 09-30-2020 to 10-14-2020.
        # "tqdm.tqdm()" used to display loading status.
        for index, account in tqdm.tqdm(twitter_accounts.iterrows(), total=num_accounts):
            # API URL to acquire data from a specific Twitter account.
            url = f"https://api.twitter.com/2/users/{account['id']}/tweets?user.fields=created_at,description"\
                + ",entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics"\
                + ",url,username,verified&max_results=100&start_time=2020-09-30T00:00:00Z&end_time=2020-10-15T00:00:00"\
                + "Z&expansions=&tweet.fields=created_at,public_metrics,source,text"
            
            # Send a GET response to the API using the URL and bearer token credentials
            response = get(url, headers=credentials)
            
            # Set 3 second delay between each GET request
            sleep(3)

            # Use json.loads() to index into the `data` key of the response object.
            # Encode from bytes to UTF-8
            tweets = json.loads(response.text.encode('UTF-8'))['data']

            # Extract the information from each tweet and store it as a row in `df`.
            for tweet in tweets:
                tweet_data = tweet_info(account=account, tweet=tweet)
                df = pd.concat([df, tweet_data])
                
        # Sort the tweets by Timestamp
        df = df.sort_values(by=['post_time']).reset_index(drop=True)
        
        # Create a new column to store user engagement per Tweet
        df = df.assign(
            total_engagement = df[['retweet_count', 'reply_count', 'like_count', 'quote_count']].sum(axis=1)
        )
        
        # Cache the dataframe as a CSV file in the local directory.
        df.to_csv(filename, index=False)
        
        # Return Twitter datav
        return df
    else:
        # Return Twitter data
        return cache

    
####################################### Acquire News Article Data ######################################
def url_request(url):
    '''
    Accepts a URL
    Returns a response object
    '''
    headers = {"User-Agent": "Promeos"}
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
    cache = check_local_cache(file=file_name)
    
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
