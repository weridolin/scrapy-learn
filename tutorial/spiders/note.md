# 基础概念--Spider

- 继承自 ``scrapy.Spider``

## 运行的过程
1. 定义一些初始urls ->`` start_urls ``,运行时首先会调用
``start_requests() ``方法,运行时依次爬取初始urls。
2. callback 默认为 ``parse`` 方法，在回调函数中，
你解析响应(网页)并返回项对象、请求对象或这些
对象的可迭代对象。这些请求也将包含一个回调(可能是相同的)
，然后将由Scrapy下载，然后由指定的回调处理它们的响应，(爬取下一页也是在这里)
3. 返回数据后，交给pipeline处理


## scrapy.Spider
- name

唯一的，可以实例化多个，一般命名为domain

- allowed_domains

允许的域名，必须配合``OffsiteMiddleware=True``


- custom_settings

over_write project setting,类型为一个字典，必须设置为一个
类属性， 因为设置是在实例化之前更新的


- settings

Spider的配置，为settings的实例

- logger

spider logger

- from_crawler()

__init__的代理方法,创建一个spider

Parameters

        crawler (Crawler instance) – crawler to which the spider will be bound

        args (list) – arguments passed to the __init__() method

        kwargs (dict) – keyword arguments passed to the __init__() method

- start_requests()-> [iterator of spider.Requests]

spider 开始运行时会调用的方法
generates Request(url, dont_filter=True) for each url in start_urls.


- parse() -> [iterator of request or item objects]

Parameters

    response (Response) – the response to parse

处理scrapy爬取的response

- log
spider logger的装饰器

- close（）
spider close时会调用这个方法


## demo
```python
import scrapy

class MySpider(scrapy.Spider):
    name = 'example.com'
    allowed_domains = ['example.com']
    start_urls = [
        'http://www.example.com/1.html',
        'http://www.example.com/2.html',
        'http://www.example.com/3.html',
    ]

    def parse(self, response):
        for h3 in response.xpath('//h3').getall():
            yield {"title": h3}
            # yield MyItem(title=h3)

        for href in response.xpath('//a/@href').getall():
            yield scrapy.Request(response.urljoin(href), self.parse)




```
