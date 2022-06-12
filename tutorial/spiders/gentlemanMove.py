import base64
import json,os,re
from requests import JSONDecodeError
import scrapy
from tutorial.items import GentleManMovieItem
from tutorial.database.models import GentleManMoveModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


MADOULAHEADER={
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    # "accept-encoding":"gzip, deflate, br",
    "accept-language":"zh-CN,zh;q=0.9",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}
PUBLIC_COMPANY=[]



class MADOULAMovSpider(scrapy.Spider):
    name = "gentleman_mov"

    urls = [
        "https://madouse.la/index.php/vod/type/id/1/page/1.html"
    ]
    domain = "https://madouse.la"
    all_domains=["https://madouse.la"]
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'tutorial.pipelines.GentleManDownPipeline': 200,
            'tutorial.pipelines.GentlemanDataBasePipeline': 300
        },
        'MEDIA_ALLOW_REDIRECTS' : True,
        'LOG_LEVEL':"INFO",
        'HTTPERROR_ALLOWED_CODES' :[301,302],
        # 'DOWNLOADER_MIDDLEWARES':{
        #     "tutorial.middlewares.SeleniumMiddleware":999
        # }
    }
    headers={
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    # "accept-encoding":"gzip, deflate, br", # 添加了话响应会被压缩，要先解压缩在解码
    "accept-language":"zh-CN,zh;q=0.9",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }   

    item = GentleManMovieItem
    db_model = GentleManMoveModel
    db_unique_field = "m3u8_index_url"
    # 1 先获取每一页的作品
    # 2 获取作品里面一步的视频文件
    use_selenium = True

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.driver =None

    def start_requests(self):
        self.logger.info(f">>> madou move spider start --> header:{self.headers}")
        os.environ.setdefault("http_proxy","http://127.0.0.1:4780")
        os.environ.setdefault("https_proxy","https://127.0.0.1:4780")
        self.engine = create_engine(self.settings.get("DB_URI"))
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        ### SELENIUM
        if self.use_selenium:
            self.logger.info(">>> use selenium,selenium init")
            options = FirefoxOptions()
            # options.add_argument('--proxy-server=http://127.0.0.1:4780')
            options.binary_location =r"C:\Program Files\Mozilla Firefox\firefox.exe"
            options.headless = True
            options.page_load_strategy = "eager"
            self.driver = webdriver.Firefox(options=options,executable_path=os.path.join(os.path.dirname(__file__),"geckodriver.exe"))
            self.driver.get("http://www.baidu.com")
        for url in self.urls:
            yield scrapy.Request(
                url=url,
                callback=self.page_parse,
                headers=self.headers
            )  

    def page_parse(self, response, **kwargs):
        """解析每一页的所有作品,找出要下载的作品和作品的详情页"""
        # print(response.meta,response.url)
        # return
        move_list = "//ul[@class='content-list']/li/div[@class='li-bottom']/h3/a"
        move_list = response.xpath(move_list)
        for item in move_list:
            detail_href,move_title = item.attrib['href'],item.attrib['title']
            # self.logger.info(f">>>get move --> [{self.domain}{detail_href}]")
            movie_src_url=f"{self.domain}{detail_href}"
            if not self.is_exist(movie_src_url=movie_src_url):
                item: GentleManMovieItem=GentleManMovieItem(
                    title=move_title,
                    series= self.get_series(move_title),
                    movie_src_url=movie_src_url,
                )
                if not self.use_selenium:
                    yield scrapy.Request(
                        url=f"{self.domain}{detail_href}",
                        callback=self.get_movie_detail,
                        cb_kwargs={"item":item},
                        headers=self.headers
                    )
                else:
                    self.driver.get(movie_src_url)
                    _ = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="video"]/div'))) 
                    e = self.driver.find_element(By.XPATH,'//*[@id="playleft"]/iframe')
                    play_url = e.get_attribute("src")
                    self.logger.info(f">>> get m3u8 src url by selenium:{play_url}")
                    m3u8_index_url = play_url.split("=")[1]
                    item.m3u8_index_url = m3u8_index_url
                    yield scrapy.Request(
                        url=m3u8_index_url,
                        headers=self.headers,
                        callback=self.get_move_ts_url_list_from_index,
                        cb_kwargs={"item":item,"url":m3u8_index_url}
                    )
                    # SCRAPY只能返回 REQUEST/ITEM/NONE?
                    # gen = self.get_move_detail_by_selenium(url = movie_src_url,item=item)                
                    # gen.send(None)
            else:
                self.logger.info(f"urc:{movie_src_url} is already exist!")
        try:
            series_next_page = response.xpath("//div[@class='pages']/a[@class='a1' and contains(text(),'下一页')]").attrib['href']
            self.logger.info(f"get series next page:{series_next_page}")
            if series_next_page:
                yield scrapy.Request(
                    url=f"{self.domain}{series_next_page}",
                    callback=self.page_parse,
                    headers=self.headers)
        except KeyError:
            self.logger.info("no more pages")

    def get_movie_detail(self, response, item:GentleManMovieItem,**kwargs): 
        """
            获取每部影片的 M3U8 信息
        """
        # src跨 iframe,这里从script里面拿 mu3m8 detail //*[@id="video"]/script[1]
        script = response.xpath('//div[@class="play"]/div[@class="p_movie"]/div[@id="video"]/script/text()').extract_first()
        try:
            args = json.loads(script.split("=")[1])
        except JSONDecodeError:
            self.logger.error(f">>> get script error --> [{script}]")
        m3u8_index_url = args.get("url",None)
        # self.logger.info(f">>> get move index src url --> {m3u8_index_url}")
        item.m3u8_index_url = m3u8_index_url
        yield scrapy.Request(
            url=m3u8_index_url,
            headers=self.headers,
            callback=self.get_move_ts_url_list_from_index,
            cb_kwargs={"item":item,"url":m3u8_index_url}
        )

    def get_move_detail_by_selenium(self,url,item:GentleManMovieItem,**kwargs):
        ## 用selenium 模拟获取iframe里面的连接。而不是从script脚本里面获取
        self.driver.get(url)
        _ = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="video"]/div'))) 
        e = self.driver.find_element(By.XPATH,'//*[@id="playleft"]/iframe')
        play_url = e.get_attribute("src")
        self.logger.info(f">>> get m3u8 src url by selenium:{play_url}")
        m3u8_index_url = play_url.split("=")[1]
        item.m3u8_index_url = m3u8_index_url
        yield scrapy.Request(
            url=m3u8_index_url,
            headers=self.headers,
            callback=self.get_move_ts_url_list_from_index,
            cb_kwargs={"item":item,"url":m3u8_index_url}
        )



    def get_move_ts_url_list_from_index(self, response, item:GentleManMovieItem,**kwargs):
        res = []
        prefix = item.m3u8_index_url.rsplit("/",1)[0]
            ## index里面其他索引,新的请求地址为 域名+file
            ## https://v5.szjal.cn 会重定向到  https://e4.monidai.com
            ## index 里面为真正的源index
        # if "https://v5.szjal.cn" in item.m3u8_index_url:
        for file in response.text.split("\n"):
            if file.strip().endswith("m3u8"):# 文件里面为真正的源  
                new_url = response.url
                new_host =  re.search(r"[a-zA-z]+://[^\s]*?/",new_url).group()
                new_m3u8_index_url = f"{new_host}/{file}"
                item.m3u8_index_url = new_m3u8_index_url
                self.logger.info(f">>> new redirect url:{new_m3u8_index_url}")
                yield scrapy.Request(
                    url=new_m3u8_index_url,
                    headers=self.headers,
                    callback=self.get_move_ts_url_list_from_index,
                    cb_kwargs={"item":item,"url":new_m3u8_index_url}
                )
    # else: 
        # for file in response.text.split("\n"):
            else:
                file:str = file.strip()
                if file.strip().endswith("ts"):
                    res.append(f"{prefix}/{file}")   
                elif file.startswith("http"):
                    res.append(file)
        item.m3u8_ts_url_list = res
        yield item

    def get_series(self,title:str):
        title = base64.b64encode(title.encode())
        if b"6bq76LGG5Lyg5aqS" in title:
            return "MD"
        elif b"57K+5Lic" in title:
            return "JD"
        elif b"5p6c5Ya7" in title:
            return "GD"
        elif b"57OW5b+D" in title:
            return "TX"
        elif b"6JCd6I6J56S+" in title:
            return "LYS"
        else:
            return "UNDEFINED"

    def is_exist(self, movie_src_url):
        record = self.session.query(GentleManMoveModel).filter(
            GentleManMoveModel.movie_src_url == movie_src_url).first()
        if record:
            return True
        return False  



if __name__ == "__main__":
    options = FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    # driver.quit()