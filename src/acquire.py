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
        return data
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
        
        # The websites we want to scrape
        blog_urls = [
            'https://www.latimes.com/california/story/2020-03-16/los-angeles-parking-ticket-street-sweeping-coronavirus-covid19',
            'https://www.latimes.com/california/story/2020-10-15/street-sweeping-parking-enforcement-resumes-today',
            'https://abc7.com/society/las-resumed-parking-enforcement-prompts-outcry/7079278/'
        ]

        for url in blog_urls:
            response = url_request(url=url)
            
            requests = web_scrape_in_progress(requests=requests, response=response, start_time=start_time)
            
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('title').text
            date_published = soup.find('time', itemprop='datePublished').text
            article = soup.find('div', class_='jupiterx-post-content').text

            blog_posts.append({'title': title,
                               'date_published': date_published,
                               'article': article})

        pd.DataFrame(blog_posts).to_json(file_name)
        return blog_posts
    else:
        return cache
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