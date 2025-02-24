# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# example item
class SteamScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GameItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    positive_rate = scrapy.Field()
    release_date = scrapy.Field()
    developer = scrapy.Field()
    publisher = scrapy.Field()
    # tags are user defined, while genes are publiser defined
    tags = scrapy.Field()
    genes = scrapy.Field()
    price = scrapy.Field()

class GameReview(scrapy.Item):
    game_name = scrapy.Field()
    reviewer_name = scrapy.Field()
    early_access = scrapy.Field()
    recommended = scrapy.Field() #True: recommend or False: not recommend
    review_text = scrapy.Field()
    time_played = scrapy.Field()
    number_helpful = scrapy.Field()
    number_funny = scrapy.Field()
    




