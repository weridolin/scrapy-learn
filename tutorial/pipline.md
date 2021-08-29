# 接受爬取后的一个ITEM并对其进行处理

# 用法举例
- 清理数据
- 验证抓取的数据(检查项目是否包含某些字段)
- 检查副本(并删除它们)
- 存储到数据库


## process_item(self, item, spider)

- item (item object) – 抓取的item
- spider (Spider object) – 抓取item的spider

## open_spider(self, spider)
spider 开始爬出时会调用的方法

## close_spider(self, spider)
spider close时调用的方法

## from_crawler(cls, crawler)
如果pipeline定义了这个方法，pipeline的创建将会调用这个方法
从crawler创建一个新的pipeline实例
crawler对象提供了所有Scrapy核心组件的访问，
如设置和信号;它是pipeline访问它们并将其功能挂钩到Scrapy的一种方式。

Parameters
- crawler (Crawler object) – crawler that uses this pipeline

- demo
```python
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
class PricePipeline:

    vat_factor = 1.15

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('price'):
            if adapter.get('price_excludes_vat'):
                adapter['price'] = adapter['price'] * self.vat_factor
            return item
        else:
            raise DropItem(f"Missing price in {item}")
```


- json pipline
```python
import json

from itemadapter import ItemAdapter

class JsonWriterPipeline:

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item
```

- 插入数据库
from_crawler,调用spider的配置文件，调用配置文件的
相关数据库配置

```python
import pymongo
from itemadapter import ItemAdapter

class MongoPipeline:

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
```

- 过滤item重复元素

```python
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['id'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['id'])
            return item
```

# 启用pipeline -> 项目settings文件

```python
ITEM_PIPELINES = {
    'myproject.pipelines.PricePipeline': 300,
    'myproject.pipelines.JsonWriterPipeline': 800,
}
```
后面的数值代表优先级，越低表示优先级越高
