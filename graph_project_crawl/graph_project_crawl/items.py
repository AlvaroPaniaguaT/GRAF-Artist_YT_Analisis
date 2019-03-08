# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GraphProjectCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    artist_name = scrapy.Field()
    artist_id = scrapy.Field()
    song = scrapy.Field()
    feat_artist_id = scrapy.Field()

