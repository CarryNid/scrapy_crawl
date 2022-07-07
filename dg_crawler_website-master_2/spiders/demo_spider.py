# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

#author: yourName
class DemoSpiderSpider(BaseSpider):
    name = 'demo_spider'
    website_id = 0
    language_id = 0
    start_urls = ['https://www.baidu.com/']
    proxy = '02' # 如果爬虫需要代理，加上这一行成员变量，否则别加。

    def parse(self, response):
        item = NewsItem()
        item['title'] = 'title'
        item['category1'] = 'category1'
        item['category2'] = 'category2'
        item['body'] = 'body'
        item['abstract'] = 'abstract'
        item['pub_time'] = DateUtil.time_now_formate()
        item['images'] = []
        yield item
