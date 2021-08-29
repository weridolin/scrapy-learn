# response object 暴漏了 .selector属性，为Selector实例
- response.xpath()

- response.css()

```python

from scrapy.selector import Selector
body = '<html><body><span>good</span></body></html>'
Selector(text=body).xpath('//span/text()').get()
# >>>'good'


from scrapy.selector import Selector
from scrapy.http import HtmlResponse
response = HtmlResponse(url='http://example.com', body=body)
Selector(response=response).xpath('//span/text()').get()

```
- response.xpath().get() --> first match

- response.css().getall() --> all results

## 可以链式调用 --> xpath().css().....
