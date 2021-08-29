# setting 集中方式的优先级

1. Command line options (most precedence)
```scrapy crawl myspider -s LOG_FILE=scrapy.log```
2. Spider 类里面的settings
```
class MySpider(scrapy.Spider):
    name = 'myspider'

    custom_settings = {
        'SOME_SETTING': 'some value',
    }
```
3. project 的settings

 [settings.py]
 
4. Default settings per-command
``命令里面的默认设置``

5. Default global settings默认的全球设置


# 爬虫访问setting

- self.settings.attributes

```python
class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['http://example.com']

    def parse(self, response):
        print(f"Existing settings: {self.settings.attributes.keys()}")
```

- from_crawler 方法 scrapy.crawler.Crawler.settings 

```python
class MyExtension:
    def __init__(self, log_is_enabled=False):
        if log_is_enabled:
            print("log is enabled!")

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getbool('LOG_ENABLED'))
```
