'''
Descripttion: 
version: 
Author: lhj
Date: 2021-08-20 21:09:20
LastEditors: lhj
LastEditTime: 2021-09-03 00:21:27
'''
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.http import headers
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from types import FrameType
from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tutorial.database.models import DouBanMovieComment as DBMovieModel, GentleManResourceModel
from tutorial.items import DouBanMovieComment, GentleManResourceItem
import scrapy
import os


class TutorialPipeline:
    def process_item(self, item, spider):
        return item


class DataBasePipeline:
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.engine = create_engine(db_uri)
        self.Session = sessionmaker(bind=self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(db_uri=crawler.settings.get("DB_URI"))

    def open_spider(self, spider):
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()

    def process_item(self, item: DouBanMovieComment, spider):
        if not self.is_exist(item, spider):
            new = DBMovieModel(
                name=item.name,
                score=item.score,
                summary=item.summary,
                score_update_time=item.score_update_time
            )
            self.session.add(new)
        # spider.logger.info(f">>>>>>{item.summary}")
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return item

    def is_exist(self, item: DouBanMovieComment, spider):
        record: DBMovieModel = self.session.query(DBMovieModel).filter(
            DBMovieModel.name == item.name).first()
        spider.logger.info(f">>>>>>{record}")
        if record:
            record.name = item.name
            record.summary = item.summary
            record.score = item.score
            record.score_update_time = item.score_update_time
            self.session.commit()
            return True
        return False


class GentleManDownPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item: GentleManResourceItem = None):
        return os.path.join(item.series_type,item.series_id, f"{item.flag}.jpg")

    def get_media_requests(self, item: GentleManResourceItem, info):
        if item.src_url:
            self.spiderinfo.spider.logger.info(f"begin down item >>>>{item}")
            yield scrapy.Request(url=item.src_url, headers=
                {
                    "Referer": "https://www.mzitu.com/",
                    'Accept': 'image/webp,*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                }
            )

    def item_completed(self, results, item: GentleManResourceItem, info):
        self.spiderinfo.spider.logger.info(f"results ---> {results}")
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            # raise DropItem("Item contains no images")
            self.spiderinfo.spider.logger.error(
                f"GentleManDownPipeline drop item ---> {item}")
            return item
        # adapter = ItemAdapter(item)
        item.local_uri = os.path.join(self.spiderinfo.spider.settings.get("IMAGES_STORE"),image_paths[0])
        self.spiderinfo.spider.logger.info(f"down item complete ---> {item}")
        return item


class GentlemanDataBasePipeline():
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.engine = create_engine(db_uri)
        self.Session = sessionmaker(bind=self.engine)
        self.orm = None
        self.item = None
        self.db_unique_field=None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(db_uri=crawler.settings.get("DB_URI"))

    def open_spider(self, spider):
        self.orm = spider.db_model
        self.item = spider.item
        self.db_unique_field = spider.db_unique_field
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()
        spider.driver.quit()

    def process_item(self, item, spider):
        # spider.logger.info(f">>> process item ->{item.to_dict()}")
        if not self.is_exist(item):
            new = self.orm(**item.to_dict())
            self.session.add(new)
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return item

    def is_exist(self, item):
        record = self.session.query(self.orm).filter(getattr(self.orm,self.db_unique_field) == getattr(item,self.db_unique_field)).first()
        # spider.logger.info(f">>>>>>{record}")
        if record:
            for k,v in item.to_dict().items():
                if hasattr(record,k):
                    setattr(record,k,v)
            self.session.commit()
            return True
        return False

from scrapy.pipelines.files import FilesPipeline
class GentleManMoveDownPipeline(FilesPipeline):
    ...