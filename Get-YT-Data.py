import os
from apiclient.discovery import build
from datetime import datetime
import pandas as pd
import random
import time
import sys


YT_API_KEY = [
              '<API KEYS HERE>'
              ]

api_index = 1

def concat_files():
    files_names = ['./Data/channels_ids_1.txt', './Data/channels_ids_2.txt', './Data/channels_ids_3.txt']
    list_ids = list()
    for path in files_names:
        f = open(path, 'r', encoding='utf-8').read()
        f = f.split('\n')
        for item in f:
            if(item not in list_ids):
                list_ids.append(item)
            else:
                print('Item duplicated')
    new_f = open('./Data/full_list_channels.txt', 'w', encoding='utf-8')
    new_f.write('\n'.join(list_ids))


def main():
    '''
        This program functionality is to extract some information from Youtube API v3 for a list of artists
        These are the fields extracted:
            - channel id for each artist search (most relevant channel for an artist query)
            - playlist_id for each channel_id
            - videos name for each playlist_id
            - statistics for each channel
    '''
    # Reads artists file and stores in a list
    #artist_list = open('./Data/Lista_Artista.txt', 'r', encoding="utf-8").read()  
    #artist_list = artist_list.split("\n")
    
    # Reads CSV file with YT channels data
    df = pd.read_csv('./Data/Channels_Data.csv', encoding='utf-8', sep=';', index_col=None)
    playlist_id_list = df['playlist_id'].tolist()
    

    ## Creates an authenticated youtube object to extract data from different endpoints
    youtube = authenticate_on_youtube()
    extract_channel_videos(playlist_id_list, youtube)
    #get_channel_data(channelIDs_list, youtube)

    ## Used to extract channel IDs and store it in a file
    #extract_channels_id(artist_list, youtube)

    #playlists_ids = get_playlists_ids(channel_ids, youtube)         # 
    #videos_list, videos_ids = get_videos_names(playlists_ids, youtube)
    #stats = get_video_statistics(videos_ids, youtube)
    #print(stats)

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
    i = 0
    channels_file = open('./Data/channels_ids_3.txt', 'w', encoding='utf-8')
    for artist in artist_list:  
        print('Iteration %s, requesting channel for --> %s' % (artist, str(i)))

        try:
            channel_name = do_request(artist, youtube)
        except Exception as e:
            print("Exceeded quota on Youtube account, changing api key")
            youtube = authenticate_on_youtube()
            channel_name = do_request(artist, youtube)

        channels_file.write(channel_name)
        channels_file.write('\n')
        sleep_random_time()
        i += 1 # Simple counter to know the position of the artist list
    channels_file.close()


def do_request(artist, youtube):
    ## Getting the most relevant channel for a given artist
    request = youtube.search().list(q=artist.upper(), part='snippet', 
                                    type='channel', maxResults=1, 
                                    order='viewCount').execute()
    try:
        ID = request['items'][0]['snippet']['channelId']
    except Exception as e:
        print(request)
        ID = ""      
    return ID

# This function throttles the code to not be identified as bot by Google
def sleep_random_time():
    rand_secs = random.randint(1, 10)
    print("Sleeping %s seconds" % str(rand_secs))
    time.sleep(rand_secs)

# This function extracts channel data from different endpoints and stores in pandas dataframe object
def get_channel_data(channel_ids_list, youtube):
    df_result = pd.DataFrame()
    list_playlistIDs = list()
    for channel_id in channel_ids_list:
        # Request quota = 7
        response = youtube.channels().list(id=channel_id,
                                         part='snippet,contentDetails,statistics').execute()

        # Store some data from response
        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        viewCount = response['items'][0]['statistics']['viewCount']
        subscriberCount = response['items'][0]['statistics']['subscriberCount']
        channel_title = response['items'][0]['snippet']['title']
        data = {
            'channel_id': [channel_id],
            'channel_title': [channel_title],
            'view_count': [viewCount],
            'subscriber_count': [subscriberCount],
            'playlist_id': [playlist_id]
            }
        new_row = pd.DataFrame.from_dict(data, orient='columns')
        df_result = df_result.append(new_row)
    df_result.to_csv('./Data/Channels_Data.csv', sep=";", encoding="utf-8", index=None)
    return list_playlistIDs

# Extracts videos
def extract_channel_videos(playlist_id_list, youtube):
    df_songs = pd.DataFrame()
    for playlist_id in playlist_id_list:
        print(playlist_id)
        next_page_token = None
        # Iterate for every page in playlist
        while 1:
            try:
                next_page_token, df_songs = get_videos(youtube, playlist_id, next_page_token, df_songs)
            except Exception as e:
                print("Quota exceeded, authenticating with other account")
                youtube = authenticate_on_youtube()
                next_page_token, df_songs = get_videos(youtube, playlist_id, next_page_token, df_songs)
            print(df_songs.shape)
            # Break the loop if next_page_token is none
            if next_page_token is None:
                break
            
    
    df_songs.to_csv('./Data/Repertory.csv', sep=";", encoding='utf-8', index=False)
        
def get_videos(youtube, playlist_id, next_page_token, df_songs):
    response = youtube.playlistItems().list(playlistId=playlist_id,
                                                part='snippet',
                                                maxResults=50,
                                                pageToken=next_page_token).execute()
    try:
        next_page_token = response['nextPageToken']
    except Exception as e:
        next_page_token = None

    items = response['items']
    for item in items:
        song_title = item['snippet']['title']
        data = {
            'playlist_id': [playlist_id],
            'song_title': [song_title]
        }
        new_row = pd.DataFrame.from_dict(data, orient='columns')
        df_songs = df_songs.append(new_row, ignore_index=True)
    return next_page_token, df_songs
        


main()