# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tutorial.database.models import DouBanMovieComment as DBMovieModel
from tutorial.items import DouBanMovieComment

class TutorialPipeline:
    def process_item(self, item, spider):
        return item



class DataBasePipeline:
    def __init__(self,db_uri):
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

    def process_item(self, item:DouBanMovieComment, spider):
        if not self.is_exist(item,spider):
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

    def is_exist(self,item:DouBanMovieComment,spider):
        record:DBMovieModel = self.session.query(DBMovieModel).filter(DBMovieModel.name==item.name).first()
        spider.logger.info(f">>>>>>{record}")
        if record:
            record.name =item.name
            record.summary = item.summary
            record.score = item.score
            record.score_update_time = item.score_update_time
            self.session.commit()
            return True
        return False
