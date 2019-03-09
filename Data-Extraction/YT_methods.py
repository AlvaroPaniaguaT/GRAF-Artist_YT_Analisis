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


def extract_channels_id(artist_list, youtube, tmp_filepath):
    '''
        This functions extracts channels names for the artist_list from
        Youtube and saves them in channels.txt file
    '''
    channels_name_list = list()
    channels_id_list = list()
    channels_file = open(tmp_filepath, 'w', encoding='utf-8')
    for artist in artist_list:  
        print('Requesting channel for --> %s' % (artist))

        try:
            channel_id, channel_name = search_channel(artist, youtube)
        except Exception as e:
            print("Exceeded quota on Youtube account, changing api key")
            youtube = authenticate_on_youtube()
            channel_id, channel_name = search_channel(artist, youtube)

        channels_name_list.append(channel_name)
        channels_id_list.append(channel_id)
        print(len(channels_name_list), len(channels_id_list))
        channels_file.write(channel_name)
        channels_file.write('\n')
        sleep_random_time()
    channels_file.close()
    return channels_name_list, channels_id_list, youtube

## Gets the most viewed channel for a given artist
def search_channel(artist, youtube):
    
    request = youtube.search().list(q=artist.upper(), part='snippet', 
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
def get_channel_data(row, youtube):
    channel_id = row['channel_id']
    # Request quota = 7
    response = youtube.channels().list(id=channel_id,
                                       part='snippet,contentDetails,statistics').execute()

    # Store some data from response
    row['view_count'] = response['items'][0]['statistics']['viewCount']
    row['subs_count'] = response['items'][0]['statistics']['subscriberCount']

    return row
