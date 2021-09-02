'''
Descripttion: 
version: 
Author: lhj
Date: 2021-08-31 07:37:53
LastEditors: lhj
LastEditTime: 2021-09-03 00:47:25
'''

import re
import scrapy
from tutorial.items import GentleManResourceItem


class GentleManSpider(scrapy.Spider):
    name = "gentleman"

    urls_series = [
        ('https://www.mzitu.com/xinggan/', '性感'),
        # ('https://www.mzitu.com/japan/', '日本'),
        # ('https://www.mzitu.com/mm/', '清纯'),
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.GentleManDownPipeline': 200,
            'tutorial.pipelines.GentlemanDataBasePipline': 300
        },
        'MEDIA_ALLOW_REDIRECTS' : True
    }

    def start_requests(self):
        # 1 先获取每个系列的链接
        # 2 在获取每个系列里面每张图的链接
        for item in self.urls_series:
            url, series_type = item
            yield scrapy.Request(
                url=url,
                callback=self.series_parse,
                cb_kwargs={"series_type":series_type}
            )

    def series_parse(self, response, **kwargs):
        """解析各个系列中的每一套作品"""
        series_detail_urls = response.xpath(
            "/html/body/div[2]/div[1]/div[2]/ul/li/span[1]/a")
        # self.logger.info(f"series_detail_urls-->{series_detail_urls} len:{len(series_detail_urls)}")
        for item in series_detail_urls:
            self.logger.info(f"get series url:{item.attrib['href']}")
            series_id = re.search("[1-9]\d*$",item.attrib['href']).group()
            yield scrapy.Request(
                url=item.attrib['href'],
                callback=self.detail_parse,
                cb_kwargs={
                    "series_id":series_id,
                    "series_type":kwargs.get("series_type","UNKNOWN")}
            )

        series_next_page = response.css(".next").attrib['href']
        try:
            if series_next_page:
                yield scrapy.Request(
                    url=series_next_page,
                    callback=self.series_parse)
                self.logger.info(f"get series next page:{series_next_page}")
        except KeyError:
            self.logger.info("no more series")

    def detail_parse(self, response, **kwargs):
        """解析每套作品的每一张图，返回ITEM
        request_header refere - https://www.mzitu.com/
        """
        src_url = response.css(".blur").attrib["src"]
        # 每个系列对应的顺序，比如 XX-X XX第X张 [0-9]*$
        series_order_number = re.search("[0-9]*$",response.url).group() or 1
        series_id=kwargs.get("series_id",None)
        if series_id:
            flag = "{0}-{1}".format(str(series_id),str(series_order_number)) 
        else:
            flag = "{0}-{1}".format(str("undefined"),str(series_order_number)) 

        item = GentleManResourceItem(
            title = response.xpath("//h2/text()").get(),
            url=response.url,
            series_id=series_id,
            series_type=kwargs.get("series_type","UNKNOWN"),
            src_url=src_url,
            flag = flag
        )
        # self.logger.info(f"get pic--> series:{kwargs.get('series')},src url:{src_url}")
        yield item            
        try:
            detail_next_url = response.xpath("//a/span[text()='下一页»']/parent::*").attrib["href"]
            yield scrapy.Request(
                url=detail_next_url,
                callback=self.detail_parse,
                cb_kwargs={
                    "series_id":series_id,
                    "series_type":kwargs.get("series_type","UNKNOWN")
                    })
        except KeyError:
            self.logger.info(f"{kwargs.get('series')} get pics src url finish")
        
        