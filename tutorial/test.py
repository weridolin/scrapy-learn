'''
Descripttion: 
version: 
Author: lhj
Date: 2021-09-01 01:24:31
LastEditors: lhj
LastEditTime: 2021-09-02 19:45:41
'''

# import m3u8

# proxies = {
#     'http': 'http://127.0.0.1:4780',
#     'https': 'http://127.0.0.1:4780',
# }

# http_client = m3u8.httpclient.DefaultHTTPClient(proxies)
# playlist = m3u8.load('https://v5.szjal.cn/20210706/8bn40IUJ/index.m3u8', http_client=http_client)  # this could also be an absolute filename
# print(playlist.dumps(),playlist.)

# import requests
# res= requests.get("https://v5.szjal.cn/20210706/8bn40IUJ/index.m3u8",proxies=proxies)
# print(res.text)

from operator import index
import os
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

if __name__ == "__main__":
    options = FirefoxOptions()
    options.binary_location =r"C:\Program Files\Mozilla Firefox\firefox.exe"
    options.headless = True
    options.page_load_strategy = "eager"
    driver = webdriver.Firefox(options=options,executable_path=os.path.join(os.path.dirname(__file__),"spiders","geckodriver.exe"))
    r = driver.get(r"https://madouse.la/index.php/vod/play/id/142093/sid/1/nid/1.html")
    # try:
    print(">>>> load finish")
    elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="video"]/div'))) 
    e = driver.find_element(By.XPATH,'//*[@id="playleft"]/iframe')
    play_url = e.get_attribute("src")
    index_src_url = play_url.split("=")[1]
    print(">>>>> load finish",index_src_url)
        # elem = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.XPATH, "//*[@id='install']"))
    # finally:
    #     driver.quit()