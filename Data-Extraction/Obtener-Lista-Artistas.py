from lxml import html
import requests
import pandas as pd
import random
import time
import sys
from YT_methods import *
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http.request import Request


# This function extracts a list of artists
def get_artist_list(url):
    req = requests.get(url)
    tree = html.fromstring(req.content)
    output = list()
    artist_list = tree.xpath('//div/div[2]/a')

    artist_file = open('./tmp/Lista_Artista.txt', 'w', encoding='utf-8')
    print("Writing %s artists." % str(len(artist_list)))
    for artist_name in artist_list:
        output.append(artist_name.text)
        artist_file.write(artist_name.text)
        artist_file.write('\n')
    
    return output

class GraphProjectCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    artist_name = scrapy.Field()
    artist_id = scrapy.Field()
    channel_name = scrapy.Field()
    channel_id = scrapy.Field()
    view_count = scrapy.Field()
    subs_count = scrapy.Field()
    song = scrapy.Field()
    feat_artist_id = scrapy.Field()
    feat_artist_name = scrapy.Field()

class AllmusicSpider(scrapy.Spider):
    name = 'allmusic_spider'
    start_urls = ['https://www.allmusic.com']

    headers = {'User-Agent': 'MR ROBOT'} # This is a joke from Mr Robot TV serie

    # Read and store artist list
    artist_list = ""
    df = pd.DataFrame()
    endpoint_artist = 'search/artists/'
    abcd = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def __init__(self, df):
        self.df = df
        self.log(self.df.head())

    def start_requests(self):
        self.log("------Starting request process------")
        self.log(self.artist_list)
        for url in self.start_urls:
            yield Request(url, headers=self.headers)


    def parse(self, response):
        url = response.url
        for _, row in self.df.iterrows():
            composed_url = url + '/' + self.endpoint_artist + row['artist_name'].replace(' ', '+')
            dict_row = row.to_dict()
            yield Request(composed_url, 
                          headers=self.headers, 
                          callback=self.get_first_artist, 
                          meta=dict_row)

    def get_first_artist(self, response):
        meta_dict = response.meta
        next_url = response.selector.xpath('//li/div/div/a/@href').get()
        identifier = next_url.rsplit('-',1)[-1]
        meta_dict['artist_id'] = identifier
        for letter in self.abcd:
            composed_url = next_url + '/songs/all/' + letter

            yield Request(composed_url, 
                          headers=self.headers, 
                          callback=self.get_songs, 
                          meta=meta_dict)

    def get_songs(self, response):
        meta_dict = response.meta
        output_item = GraphProjectCrawlItem()
        output_item['artist_name'] = response.meta['artist_name']
        output_item['artist_id'] = response.meta['artist_id']
        output_item['channel_name'] = response.meta['channel_name']
        output_item['channel_id'] = response.meta['channel_id']
        output_item['view_count'] = response.meta['view_count']
        output_item['subs_count'] = response.meta['subs_count']
        for item in response.selector.xpath('//div[@class="title"]/a/text()'):
            song = item.get()
            output_item['song'] = song
            try:
                feat_artist_id = response.selector.xpath('//div[@class="title"]/span/a/@href').get()
                feat_artist_id = feat_artist_id.rsplit('-', 1)[-1]
                feat_artist_name = response.selector.xpath('//tbody/tr/td/div/span/a/text()').get()

            except Exception as e:
                continue
            output_item['feat_artist_id'] = feat_artist_id
            output_item['feat_artist_name'] = feat_artist_name
            yield output_item


if __name__ == "__main__":
    # Number of artists to use to extract YT channels data.
    num_artist = input('Indica el número de artistas para sacar sus datos --> ')
    
    # Read from console YT API KEYS to use
    list_YT_keys = input('Inserta una lista de claves de YT (separadas por coma) --> ')
    list_YT_keys = list_YT_keys.split(',')
    set_API_keys(list_YT_keys)

    # Step 1: Extract a list of artists for the page www.todomusica.org
    artist_list = get_artist_list('https://www.todomusica.org/listado-artistas.shtml')

    # Filter list 0 to num artist
    filtered_list = artist_list[0:int(num_artist)]
    

    # Authenticate on YOUTUBE API
    youtube = authenticate_on_youtube()

    channel_name_list, channel_id_list, youtube = extract_channels_id(filtered_list, youtube, './tmp/channels_name.txt')
    
    df_results = pd.DataFrame(data={
        'artist_name': filtered_list,
        'channel_name': channel_name_list,
        'channel_id': channel_id_list
    })

    df_results = df_results.apply(lambda x: get_channel_data(x, youtube), axis=1)

    # Crawl allmusic and output on Data.json
    process = CrawlerProcess({
        'FEED_URI': '50_First_Artists.json'
    })
    process.crawl(AllmusicSpider, df_results)
    process.start()