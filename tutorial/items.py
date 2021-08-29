# Define here the database for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class Product(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    tags = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)

# product = Product(name='Desktop PC', price=1000)
# print(product) >>>{'name': 'Desktop PC', 'price': 1000}
# dict object

import dataclasses
from typing import Optional
@dataclasses.dataclass
class Product2():
    name : Optional[str] = dataclasses.field(default=None)
    price : Optional[int] = dataclasses.field(default=None)
    stock : Optional[str] = dataclasses.field(default=None)
    tags : Optional[str] = dataclasses.field(default=None)
    last_updated : Optional[str] = dataclasses.field(default=None)
# product = Product2(name='Desktop PC', price=1000)
# print(product) >>Product2(name='Desktop PC', price=1000, stock=None, tags=None, last_updated=None)



class ChinaPerProvinceItem(scrapy.Item):
    GuangDong = scrapy.Field()
    GuangXi = scrapy.Field()
    FuJian = scrapy.Field()
    HaiNan = scrapy.Field()
    TaiWan = scrapy.Field()
    YunNan = scrapy.Field()
    HeNan = scrapy.Field()
    HeBei = scrapy.Field()
    HuNan = scrapy.Field()
    HuBei = scrapy.Field()
    BeiJing = scrapy.Field()
    ShangHai = scrapy.Field()

import json,datetime
class DirectiveJsonEncoder(json.JSONEncoder):
    """
        应对datetime.datetime() 对象的序列化,参考:
        https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


@dataclasses.dataclass
class DouBanMovieComment():
    name: Optional[str] = dataclasses.field(default=None)
    score:Optional[float] = dataclasses.field(default=None)
    summary:Optional[str] = dataclasses.field(default=None)
    score_update_time: Optional[datetime.datetime] = dataclasses.field(default=None)


    def __str__(self):
        return json.dumps(self.__dict__,ensure_ascii=False,cls=DirectiveJsonEncoder)
