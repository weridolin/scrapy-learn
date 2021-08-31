'''
Descripttion: 
version: 
Author: lhj
Date: 2021-08-31 07:37:53
LastEditors: lhj
LastEditTime: 2021-09-01 01:32:20
'''

import re
import scrapy


class GentleManSpider(scrapy.Spider):
    name = "gentleman"

    urls_series = [
        ('https://www.mzitu.com/xinggan/', '性感'),
        # ('https://www.mzitu.com/japan/', '日本'),
        # ('https://www.mzitu.com/mm/', '清纯'),
    ]

    def start_requests(self):
        # 1 先获取每个系列的链接
        # 2 在获取每个系列里面每张图的链接
        for item in self.urls_series:
            url, series = item
            yield scrapy.Request(
                url=url,
                callback=self.series_parse
            )

    def series_parse(self, response, **kwargs):
        """解析各个系列中的每一套作品"""
        series_detail_urls = response.xpath(
            "/html/body/div[2]/div[1]/div[2]/ul/li/span[1]/a")
        # self.logger.info(f"series_detail_urls-->{series_detail_urls} len:{len(series_detail_urls)}")
        for item in series_detail_urls:
            self.logger.info(f"get series url:{item.attrib['href']}")
            series = re.search("[1-9]\d*$",item.attrib['href']).group()
            yield scrapy.Request(
                url=item.attrib['href'],
                callback=self.detail_parse,
                cb_kwargs={"series":series}
            )

        # series_next_page = response.css(".next").attrib['href']
        # try:
        #     if series_next_page:
        #         yield scrapy.Request(
        #             url=series_next_page,
        #             callback=self.series_parse)
        #         self.logger.info(f"get series next page:{series_next_page}")
        # except KeyError:
        #     self.logger.info("no more series")

    def detail_parse(self, response, **kwargs):
        """解析每套作品的每一张图，返回ITEM"""
        src_url = response.css(".blur").attrib["src"]
        self.logger.info(f"get pic--> series:{kwargs.get('series')},src url:{src_url}")
        try:
            detail_next_url = response.xpath("//a/span[text()='下一页»']/parent::*").attrib["href"]
            yield scrapy.Request(
                url=detail_next_url,
                callback=self.detail_parse,
                cb_kwargs={"series":kwargs.get('series')})
        except KeyError:
            self.logger.info(f"{kwargs.get('series')} get pics src url finish")
        
        