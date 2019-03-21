import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http.request import Request
from YT_methods import *
import re

class GraphProjectCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    artist_name = scrapy.Field()
    genre = scrapy.Field()
    song = scrapy.Field()
    feat_artist_name = scrapy.Field()
    grade = scrapy.Field()


class MetroLyricsSpider(scrapy.Spider):
    name = 'metrolyric_spider'
    start_urls = 'http://www.metrolyrics.com/'

    headers = {'User-Agent': 'MR ROBOT'} # This is a joke from Mr Robot TV serie
    abcd = ['1' ,'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    pagination_dict = {}

    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }

    def start_requests(self):
        self.log("------Starting request process------")
        for item in self.abcd:
            self.pagination_dict[item.lower()] = 0
            url = self.start_urls + 'artists-%s.html' % item.lower()
            yield Request(url, headers=self.headers)
    

    def parse(self, response):
        next_pages = [url.get() for url in response.xpath('//div/p/span/a/@href')]
        if response.url in next_pages:
            index = next_pages.index(response.url) + 1
        else:
            index = 0
        try:
            # Used to paginate over each letter
            next_url = next_pages[index]
        except Exception as e:
            next_url = None
        
        # Get music genre, artist_name and call 'parse_artist_features to extract feat songs
        for artist_row in response.xpath('//table/tbody/tr'):
            classes = artist_row.xpath('td/span[contains(@class,"bar")]').xpath('@class').get().split(' ')
            grade = self.parse_evaluation(classes[-1])

            if grade >= 5:
                data = artist_row.xpath('td')
                artist_name = data[0].xpath('a/text()').get().replace('Lyrics', "")
                artist_subpath = artist_name + 'featured.html'
                artist_subpath = artist_subpath.replace(' ', '-')
                artist_url = self.start_urls + '/' + artist_subpath.lower()
                genre = data[1].xpath('text()').get()

                # yield request with additional data
                yield Request(url=artist_url, callback=self.parse_artist_features, meta={'genre': genre, 'grade': grade, 'artist_name': artist_name})
        
        if next_url:
            yield Request(url = next_url, callback=self.parse)
                
            
    def parse_artist_features(self, response):
        item = GraphProjectCrawlItem()
        item['genre'] = response.meta['genre']
        item['grade'] = response.meta['grade']
        item['artist_name'] = response.meta['artist_name']
        for song_row in response.xpath('//tbody/tr'):
            item['song'] = song_row.xpath('./td/a/text()')[0].get()
            item['feat_artist_name'] = song_row.xpath('./td/a/text()')[1].get()
            yield item
            
    def parse_url(self, url):
        grps = re.search(r'artists-([0-9]|[a-z]).html', url, re.IGNORECASE)

        if grps:
            page_id = grps.group(1)
        return page_id
        


    def parse_evaluation(self, item_class):
        grps = re.search(r'[a-z]*([0-9]*)', item_class, re.IGNORECASE)

        ev = 0
        if grps:
            ev = grps.group(1)
        return int(ev)


# Clean string registers removing tildes
def clean_registers(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
            df[col] = df[col].str.normalize('NFD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    return df

def create_empty_nodes(df):
    artist_list = list(set(df['artist_name'].tolist()))
    f_artist_list = list(set(df['feat_artist_name'].tolist()))
    for artist in f_artist_list:
        if artist not in artist_list:
            artist_list.append(artist)
            df = df.append({
                'artist_name': artist,
                'song': None,
                'genre': 'other',
                'grade': 5,
                'feat_artist_name': artist
            }, ignore_index=True)
            print(df.shape)

    return df


if __name__ == "__main__":

    # Indicate the number of artists we need to ingest data
    start_index = input('Indica el índice de inicio en la lista de artistas para sacar sus datos --> ')
    end_index = input('Indica el índice de fin en la lista de artistas para sacar sus datos --> ')

    # Start crawler and feed JSON file
    #process = CrawlerProcess({
    #    'FEED_URI': 'Artist_relations.json'
    #})
    #process.crawl(MetroLyricsSpider)
    #process.start()

    # Once scraper is ended load the json file to dataframe
    df = pd.read_json('Artist_relations.json', orient='records', lines=True, encoding='utf-8')
    df = df[df['grade'] >= 8]

    # Remove noise characters
    df = clean_registers(df)

    # Create register with previously non existing nodes
    #df = create_empty_nodes(df)

    # Get the list of artists non repeated
    list_nodes = list(set(df['artist_name'].tolist()))
    list_nodes = list_nodes[int(start_index):int(end_index)]

    ## Calculate requests quota from YT
    calc_YT_quota(len(list_nodes))

    ## Get a list of YT API keys and sets it in YT_methods
    list_YT_keys = input('Inserta una lista de claves de YT (separadas por coma) --> ')
    list_YT_keys = list_YT_keys.split(',')
    set_API_keys(list_YT_keys)

    # Authenticate on YOUTUBE API
    youtube = authenticate_on_youtube()

    df_yt_data = pd.DataFrame()
    for channel_n, channel_id, artist, yt in extract_channels_id(list_nodes, youtube):
        new_row = {
            'YT_channel_name': channel_n,
            'YT_channel_id': channel_id,
            'artist_name': artist
        }
        # Add new row and declare column type as string (equal object)
        df_yt_data = df_yt_data.append(new_row, ignore_index=True)
        df_yt_data['artist_name'] = df_yt_data['artist_name'].astype('object')
        youtube = yt
        print(df_yt_data.shape)
    
    df_yt_data = df_yt_data.apply(lambda x: get_channel_data(x, youtube, 'YT_channel_id'), axis=1)
    # Merge by name the YT data dataframe with df 
    graph_dataframe = df.merge(right=df_yt_data, on='artist_name', how='inner')

    graph_dataframe.to_json('Graph_data.json', orient='records')