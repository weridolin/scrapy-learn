# -*- encoding: utf-8 -*-
"""
@File           : quotes_spider.py
@Time           : 2021/8/20 21:38
@Author         : 林宏基
@Email          : 359066432@qq.com
@Software       : PyCharm
@Description    :
"""
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes" # 名称必须为唯一

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            # 必须返回一个Request的迭代器，spider将会根据这些初始Request往下执行
            # 这里遍历执行的是urls

    # 添加初始化参数 使用:scrapy crawl myspider -a category=electronics
    # def __init__(self, category=None, *args, **kwargs):
    #     super(MySpider, self).__init__(*args, **kwargs)
    #     self.start_urls = [f'http://www.example.com/categories/{category}']


    def parse(self, response, **kwargs):
        ## 每个Request 之后响应的处理Spider的start_requests方法返回的请求对象。
        # 在收到每个对象的响应后，它实例化response对象并调用与请求关联的回调方法(
        # 在本例中是parse方法)，将响应response作为参数传递

        # 为默认的callback方法，不用显示的去指定
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page,callback=self.parse)


        ## 数据传递流程
        # START_URLS=[]
        # FOR URL IN START_URLS
        #        URL-----> NEXT PAGE----->NEXT_PAGE
        #        URL-----> NEXT PAGE----->NEXT_PAGE
        #        ......

#
# from scrapy.spiders import XMLFeedSpider
#
# class MySpider(XMLFeedSpider):
#     name = 'example.com'
#     allowed_domains = ['example.com']
#     start_urls = ['http://www.example.com/feed.xml']
#     iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
#     itertag = 'item'
#
#     def parse_node(self, response, node):
#         self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.getall()))
#
#         item = TestItem()
#         item['id'] = node.xpath('@id').get()
#         item['name'] = node.xpath('name').get()
#         item['description'] = node.xpath('description').get()
#         return item
