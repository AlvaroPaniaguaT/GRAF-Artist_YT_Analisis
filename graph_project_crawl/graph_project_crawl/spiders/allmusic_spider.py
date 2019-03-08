# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
from graph_project_crawl.items import GraphProjectCrawlItem as GPCI

class AllmusicSpiderSpider(scrapy.Spider):
    name = 'allmusic_spider'
    start_urls = ['https://www.allmusic.com']
    #headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    headers = {'User-Agent': 'MR ROBOT'} # This is a joke from Mr Robot TV serie

    # Read and store artist list
    artist_list = open('../Data/Lista_Artista.txt', 'r', encoding="utf-8").read().split('\n')
    endpoint_artist = 'search/artists/'
    abcd = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def start_requests(self):
        self.log("------Starting request process------")
        for url in self.start_urls:
            yield Request(url, headers=self.headers)


    def parse(self, response):
        url = response.url
        for artist in self.artist_list:
            composed_url = url + '/' + self.endpoint_artist + artist.replace(' ', '+')
            yield Request(composed_url, 
                          headers=self.headers, 
                          callback=self.get_first_artist, 
                          meta={'artist_name': artist})

    def get_first_artist(self, response):
        next_url = response.selector.xpath('//li/div/div/a/@href').get()
        identifier = next_url.rsplit('-',1)[-1]
        for letter in self.abcd:
            composed_url = next_url + '/songs/all/' + letter

            yield Request(composed_url, 
                          headers=self.headers, 
                          callback=self.get_songs, 
                          meta={'artist_id': identifier, 'artist_name': response.meta['artist_name']})

    def get_songs(self, response):
        output_item = GPCI()
        output_item['artist_id'] = response.meta['artist_id']
        output_item['artist_name'] = response.meta['artist_name']
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
            

    
        
