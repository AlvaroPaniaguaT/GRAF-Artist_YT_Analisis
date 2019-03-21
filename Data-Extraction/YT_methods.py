import os
from apiclient.discovery import build
from datetime import datetime
import random
import time


YT_API_KEY = [
              '<API KEYS HERE>'
              ]

api_index = 0

# Sets user API KEYS
def set_API_keys(keys):
    global YT_API_KEY
    YT_API_KEY = keys


# Authenticates on Youtube API v.3
def authenticate_on_youtube():
    global api_index
    new_key = YT_API_KEY[api_index]
    youtube = build('youtube', 'v3', developerKey=new_key)
    api_index += 1
    return youtube


def extract_channels_id(artist_list, youtube):
    '''
        This functions extracts channels names for the artist_list from
        Youtube and saves them in channels.txt file
    '''
    for artist in artist_list:  
        print('Requesting channel for --> %s' % (artist))
        try:
            channel_id, channel_name = search_channel(artist, youtube)
        except Exception as e:
            print("Exceeded quota on Youtube account, changing api key")
            youtube = authenticate_on_youtube()
            channel_id, channel_name = search_channel(artist, youtube)


        yield channel_name, channel_id, artist, youtube

## Gets the most viewed channel for a given artist
def search_channel(artist, youtube):
    
    request = youtube.search().list(q=artist.lower() + 'VEVO', part='snippet', 
                                    type='channel', maxResults=1, 
                                    order='viewCount').execute()
    
    try:
        ID = request['items'][0]['snippet']['channelId']
        title = request['items'][0]['snippet']['title']
    except Exception as e:
        print(request)
        ID = ""
        title = "" 
    return ID, title

# This function throttles the code to not be identified as bot by Google
def sleep_random_time():
    rand_secs = random.randint(1, 10)
    print("Sleeping %s seconds" % str(rand_secs))
    time.sleep(rand_secs)

# This function extracts channel data from different endpoints and stores in pandas dataframe object
def get_channel_data(row, youtube, col_selector):
    channel_id = row[col_selector]
    print("Getting channel data for ID --> " + channel_id)
    try:
        response = youtube.channels().list(id=channel_id,
                                       part='snippet,contentDetails,statistics').execute()
    except Exception as e:
        youtube = authenticate_on_youtube()
        response = youtube.channels().list(id=channel_id,
                                       part='snippet,contentDetails,statistics').execute()
    # Store some data from response
    if response['pageInfo']['totalResults'] != 0:
        row['view_count'] = response['items'][0]['statistics']['viewCount']
        row['subs_count'] = response['items'][0]['statistics']['subscriberCount']

        return row
    else:
        return None

def calc_YT_quota(num_requests):
    search_quota = 100 * num_requests
    channels_quota = 7 * num_requests
    total_quota = search_quota + channels_quota
    print("Cuota total de peticiones al API de YT --> %s" % total_quota)
    print("Número de cuentas necesarias para hacer la ingesta --> %s" % round(total_quota/10000, 0))
