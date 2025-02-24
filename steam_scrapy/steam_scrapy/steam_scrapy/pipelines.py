# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from steam_scrapy.items import GameItem, GameReview


class SteamScrapyPipeline:

    def __init__(self) -> None:
        settings = get_project_settings()
        self.connection = psycopg2.connect(
            dbname=settings['DATABASE']['database'],
            user=settings['DATABASE']['username'],
            password=settings['DATABASE']['password'],
            host=settings['DATABASE']['host'],
            port=settings['DATABASE']['port']
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        #item received from spider
        if isinstance(item, GameItem):
            self.insert_game(item)
        elif isinstance(item, GameReview):
            self.insert_review(item)
        
        return item

    def insert_game(self, item):
        sql = """
        INSERT INTO games (name, description, positive_rate, release_date, developer, publisher, tags, genes, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                item['name'],
                item['description'],
                item['positive_rate'],
                item['release_date'],
                item['developer'],
                item['publisher'],
                item['tags'],
                item['genes'],
                item['price']
            ))
            self.connection.commit()
        except Exception as e:
            print('-- Customer LOG: Database ERROR - ', e)
            self.connection.rollback()

    def insert_review(self, item):
        sql = """
        INSERT INTO game_reviews (game_name, reviewer_name, recommended, review_text, time_played, number_helpful, number_funny, early_access)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                item['game_name'],
                item['reviewer_name'],
                item['recommended'],
                item['review_text'],
                item['time_played'],
                item['number_helpful'],
                item['number_funny'],
                item['early_access']
            ))
            self.connection.commit()
        except Exception as e:
            print('-- Customer LOG: Database ERROR - ', e)
            self.connection.rollback()


