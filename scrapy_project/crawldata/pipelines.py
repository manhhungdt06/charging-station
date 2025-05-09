# crawldata/pipelines.py
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class CrawldataPipeline:
    def __init__(self, mongodb_uri, mongodb_db):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()
        # print(item_dict)
        try:
            self.db['charging_stations'].update_one(
                {'_id': item_dict['_id']},
                {'$set': item_dict},
                upsert=True
            )
        except DuplicateKeyError:
            spider.logger.warning(f"Duplicate item found: {item_dict['_id']}")
        except Exception as e:
            spider.logger.error(f"Error processing item: {str(e)}")
        return item
