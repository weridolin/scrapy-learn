# # -*- encoding: utf-8 -*-
# """
# @File           : douban_spider.py
# @Time           : 2021/8/29 9:42
# @Author         : 林宏基
# @Email          : 359066432@qq.com
# @Software       : PyCharm
# @Description    :
# """
# import scrapy
# import datetime
# from tutorial.items import DouBanMovieComment

# class DouBanMovieCommentSpider(scrapy.Spider):
#     name = "douban" # 名称必须为唯一
#     def start_requests(self):
#         urls = ["https://movie.douban.com/top250"]
#         for url in urls:
#             yield scrapy.Request(
#                 url=url,
#                 callback=self.parse
#             )

#     def parse(self, response, **kwargs):
#         items_list_html = response.xpath("/html/body/div[3]/div[1]/div/div[1]/ol/li")
#         for index,i in enumerate(items_list_html):
#             item = DouBanMovieComment(
#                 name=i.xpath("div/div[2]/div[1]/a/span[1]/text()").get(),
#                 score=i.xpath("div/div[2]/div[2]/div/span[2]/text()").get(),
#                 summary=i.xpath("div/div[2]/div[2]/p[2]/span/text()").get(),
#                 score_update_time=datetime.datetime.now()
#             )
#             # item["name"] =i.xpath("div/div[2]/div[1]/a/span[1]/text()").get()
#             # item["score"] = i.xpath("div/div[2]/div[2]/div/span[2]/text()").get()
#             # item["comment"] = i.xpath("div/div[2]/div[2]/p[2]/span/text()").get()
#             # item["score_update_time"] = datetime.datetime.now()
#             # self.logger.info(f"{index}"*500)
#             self.logger.info(f"{item}")
#             yield item
#         try:
#             next_page = response.xpath("/html/body/div[3]/div[1]/div/div[1]/div[2]/span[3]/link").attrib['href']
#             self.logger.info(f">>> get next page :{next_page}")
#             if next_page is not None:
#                 next_page = response.urljoin(next_page)
#                 self.logger.info(f">> next page address :{next_page}")
#                 yield scrapy.Request(next_page,callback=self.parse)
#         except KeyError:
#             self.logger.info("spider finish")
