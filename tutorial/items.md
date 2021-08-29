# items
定义数据结构，类似model

##  class scrapy.item.Item([arg])

- copy()

- deepcopy()

- fields

```python
from scrapy.item import Item, Field

class CustomItem(Item):
    one_field = Field()
    another_field = Field()
```

### 可以用 Dataclass objects 
```python
from dataclasses import dataclass

@dataclass
class CustomItem:
    one_field: str
    another_field: int
```

# ITEMLOADER

## 从response 中按照规则把数据加载到item中

```python
from scrapy.loader import ItemLoader
from myproject.items import Product

def parse(self, response):
    l = ItemLoader(item=Product(), response=response)
    l.add_xpath('name', '//div[@class="product_name"]')
    l.add_xpath('name', '//div[@class="product_title"]')
    l.add_xpath('price', '//p[@id="price"]')
    l.add_css('stock', 'p#stock]')
    l.add_value('last_updated', 'today') # you can also use literal values 返回具体的值
    return l.load_item()
```

- name 由2个xpath路径决定

- 从response中提取所给规则中的数据后，调用load_item返回

## 自定义Item loader

```python
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader

class ProductLoader(ItemLoader):

    default_output_processor = TakeFirst()
    
    # 输入处理器使用_in后缀声明，而输出处理器使用_out后缀声明
    name_in = MapCompose(str.title)
    name_out = Join()

    price_in = MapCompose(str.strip)

```

- 输入处理器使用_in后缀声明，而输出处理器使用_out后缀声明





## 另外自定义item的输入/输出 processor

项目加载器包含每个(项目)字段的一个输入处理器和一个输出处理器。
一旦接收到提取的数据(通过add_xpath()、add_css()或
add_value()方法)，输入处理器就会处理它，输入处理器的结果
会被收集并保存在ItemLoader中。
收集完所有数据后，调用ItemLoader.load_item()方法来
填充和获取填充的项对象。这时输出处理器将使用先前收集的数据
调用(并使用输入处理器处理)。输出处理器的结果是最终值

- 输入必须接受一个(且仅一个)位置参数，该参数将是一个可迭代对象。

```python

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

def filter_price(value):
    if value.isdigit():
        return value

class Product(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_price),
        output_processor=TakeFirst(),
    )


from scrapy.loader import ItemLoader

il = ItemLoader(item=Product())
il.add_value('name', ['Welcome to my', '<strong>website</strong>']) #必须为可迭代对象
il.add_value('price', ['&euro;', '<span>1000</span>'])
il.load_item()
>>> {'name': 'Welcome to my website', 'price': '1000'}
```

## scrapy.loader.ItemLoader(item=None, selector=None, response=None, parent=None, **context)



## 嵌套使用 

- nested_xpath

```python
loader = ItemLoader(item=Item())
# load stuff not in the footer
# 先取出所有在标签footer下的元素
footer_loader = loader.nested_xpath('//footer')
footer_loader.add_xpath('social', 'a[@class = "social"]/@href')
footer_loader.add_xpath('email', 'a[@class = "email"]/@href')
# no need to call footer_loader.load_item()
loader.load_item()
```

## item loader 复用
```python
from itemloaders.processors import MapCompose
from myproject.ItemLoaders import ProductLoader

def strip_dashes(x):
    return x.strip('-')

class SiteSpecificLoader(ProductLoader):
    # 复用ProductLoader的name in 方法
    name_in = MapCompose(strip_dashes, ProductLoader.name_in)
```
