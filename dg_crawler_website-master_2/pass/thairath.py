# encoding: utf-8
import json

from bs4 import BeautifulSoup

import common.date
import utils.date_util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import time as t


#Author:陈卓玮
# check：凌敏 pass
class thairahSpider(BaseSpider):
    name = 'thairah'
    website_id = 1567
    language_id = 2208
    ts_now = utils.date_util.DateUtil.formate_time2time_stamp(utils.date_util.DateUtil.time_now_formate()) #获取现在时间
    list_limit = 100
    start_urls = [f'https://www.thairath.co.th/loadmore&ts={ts_now}&limit={list_limit}']###api

    def parse(self, response):
        list_data = json.loads(response.text)
        list_items = list_data['items']
        l_ts = utils.date_util.DateUtil.formate_time2time_stamp(list_items[-1]['publishTime'].split("T")[0]+" "+list_items[-1]['publishTime'].split("T")[1].split("+")[0])
        for i in list_items:
            url = i['canonical']
            time = i['publishTime'].split("T")[0]+" "+i['publishTime'].split("T")[1].split("+")[0]
            abstract = i['abstract']
            category1 = i['section']
            category2 = i['topic']
            title = i['title']
            img=[]
            img.append(i['image'])
            yield Request(url = url,callback=self.essay_parser,meta={'time':time,
                                                                    'abstract':abstract,
                                                                    'category1':category1,
                                                                    'category2':category2,
                                                                    'title':title,
                                                                    'img':img})
        if (self.time == None or l_ts >= self.time) and len(list_items) > 0:
            api = f'https://www.thairath.co.th/loadmore&ts={l_ts}&limit={self.list_limit}'
            t.sleep(10)
            # print(f"正请求{utils.date_util.DateUtil.time_stamp2formate_time(l_ts)}前的新闻列表！")
            yield Request(api)

    def essay_parser(self,response):
        soup = BeautifulSoup(response.text,'lxml')

        body=''
        for i in soup.select('p'):
            body+=i.text+'\n'

        img = response.meta['img']
        for i in soup.select('img'):
            if 'http' in i.get('src'):
               img.append(i.get('src'))

        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = body
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['time']
        item['images'] = response.meta['img']
        yield item




