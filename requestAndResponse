#  scrapy.http.Request

- url

请求的URL地址

- method

请求的方法["GET", "POST", "PUT"]


- header
请求头，key-value 形式

- body

请求body

- meta 

1. bindaddress : 绑定发起请求的IP

2. download_timeout:downloader 的等待下载时间

3. max_retry_times: 每个request的重试时间


- cb_kwargs

request callback函数的参数,key-value的形式

- replace ([url, method, headers, body, cookies, meta, flags, encoding, priority, dont_filter, callback, errback, cb_kwargs])[source]
返回一个新的request对象，如果replace的参数有更新，则替换，meta和cb_kwargs为原来的浅拷贝


# callback 函数添加额外的参数

- response object会作为callback函数的第一个参数
```python

def parse_page1(self, response):
    return scrapy.Request("http://www.example.com/some_page.html",
                          callback=self.parse_page2)

def parse_page2(self, response):
    # this would log http://www.example.com/some_page.html
    self.logger.info("Visited %s", response.url)
```

- 通过cb_kwargs进行传递

```python
def parse(self, response):
    request = scrapy.Request('http://www.example.com/index.html',
                             callback=self.parse_page2,
                             cb_kwargs=dict(main_url=response.url))
    request.cb_kwargs['foo'] = 'bar'  # add more arguments for the callback
    yield request

def parse_page2(self, response, main_url, foo):
    yield dict(
        main_url=main_url,
        other_url=response.url,
        foo=foo,
    )
```


# request　异常捕获处理

- errback参数

request 出现异常时，触发errback函数,并且将[failure](https://twistedmatrix.com/documents/current/api/twisted.python.failure.Failure.html) 作为第一个参数

```python
import scrapy

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class ErrbackSpider(scrapy.Spider):
    name = "errback_example"
    start_urls = [
        "http://www.httpbin.org/",              # HTTP 200 expected
        "http://www.httpbin.org/status/404",    # Not found error
        "http://www.httpbin.org/status/500",    # server issue
        "http://www.httpbin.org:12345/",        # non-responding host, timeout expected
        "http://www.httphttpbinbin.org/",       # DNS error expected
    ]

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.parse_httpbin,
                                    errback=self.errback_httpbin,
                                    dont_filter=True)

    def parse_httpbin(self, response):
        self.logger.info('Got successful response from {}'.format(response.url))
        # do something useful here...

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:
        
        # 根据不同的类型进行判断，参考 twisted.internet.error
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
```

- errback 添加额外参数 (cb_kwargs)

```python
def parse(self, response):
    request = scrapy.Request('http://www.example.com/index.html',
                             callback=self.parse_page2,
                             errback=self.errback_page2,
                             cb_kwargs=dict(main_url=response.url))
    yield request

def parse_page2(self, response, main_url):
    pass

def errback_page2(self, failure):
    # 通过failure.request.cb_kwargs添加额外的回调函数
    yield dict(
        main_url=failure.request.cb_kwargs['main_url'],
    )
```


# 根据某些Response停止spider的下载

- 使用sigals --> scrapy.signals

```python
import scrapy


class StopSpider(scrapy.Spider):
    name = "stop"
    start_urls = ["https://docs.scrapy.org/en/latest/"]

    @classmethod
    def from_crawler(cls, crawler):
        spider = super().from_crawler(crawler)
        crawler.signals.connect(spider.on_bytes_received, signal=scrapy.signals.bytes_received)
        return spider

    def parse(self, response):
        # 'last_chars' show that the full response was not downloaded
        yield {"len": len(response.text), "last_chars": response.text[-40:]}

    def on_bytes_received(self, data, request, spider):
        raise scrapy.exceptions.StopDownload(fail=False)

# 输出
2020-05-19 17:26:12 [scrapy.core.engine] INFO: Spider opened
2020-05-19 17:26:12 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2020-05-19 17:26:13 [scrapy.core.downloader.handlers.http11] DEBUG: Download stopped for <GET https://docs.scrapy.org/en/latest/> from signal handler StopSpider.on_bytes_received
2020-05-19 17:26:13 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://docs.scrapy.org/en/latest/> (referer: None) ['download_stopped']
2020-05-19 17:26:13 [scrapy.core.scraper] DEBUG: Scraped from <200 https://docs.scrapy.org/en/latest/>
{'len': 279, 'last_chars': 'dth, initial-scale=1.0">\n  \n  <title>Scr'}
2020-05-19 17:26:13 [scrapy.core.engine] INFO: Closing spider (finished) # 收到BYTES后触发on_bytes_received,关闭连接

```


# Response objects


- url

read-only,请求的URL

- status

请求的响应的状态码

- headers

dict,请求头

- body

response body read only

- request

response 对应的request

- meta

request.meta

- cb_kwargs
原始的 cb_kwargs


- flags

包含此响应标志的列表。标志是用于标记响应的标签。
例如:'cached'， 'redirected '等。它们被显示在
Response (__str__方法)的字符串表示法中，该方法被引擎用于日志记录

- certificate

server's SSL

- ip_address

response 对应的源IP ,只使用HTTP1.1

- protocol

该响应对应的协议，例如 “HTTP/1.0”, “HTTP/1.1”

- urljoin
