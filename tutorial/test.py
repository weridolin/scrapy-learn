'''
Descripttion: 
version: 
Author: lhj
Date: 2021-09-01 01:24:31
LastEditors: lhj
LastEditTime: 2021-09-01 01:25:34
'''
import re
item = "get series url:https://www.mzitu.com/133857"
series = re.search("[1-9]\d*$",item)
print(series.group())