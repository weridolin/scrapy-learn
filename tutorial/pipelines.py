'''
Descripttion: 
version: 
Author: lhj
Date: 2021-08-20 21:09:20
LastEditors: lhj
LastEditTime: 2021-09-02 01:39:21
'''
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from types import FrameType
from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tutorial.database.models import DouBanMovieComment as DBMovieModel
from tutorial.items import DouBanMovieComment, GentleManResourceItem
import scrapy,os


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
        if isinstance(item, GentleManResourceItem):
            spider.logger.info(f">>>>>>{item}")
            return item

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

    def file_path(self, request, response, info, *, item:GentleManResourceItem):
        return os.path.join(item.series_id,item.flag,".jpg")

    def get_media_requests(self, item, info):
        if item["src_url"]:
            self.spiderinfo.logger.info(f"begin down item >>>>{item}")
            yield scrapy.Request(url=item["src_url"])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            # raise DropItem("Item contains no images")
            self.spiderinfo.logger.error(f"GentleManDownPipeline drop item>>>{item}")
            return item
        adapter = ItemAdapter(item)
        adapter['local_uri'] = image_paths
        self.spiderinfo.logger.info(f"down item complete>>>>{item}")
        return item
