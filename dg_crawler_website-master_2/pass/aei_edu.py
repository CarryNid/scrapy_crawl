# encoding: utf-8
import html
import json

from bs4 import BeautifulSoup

import common.date
import utils.date_util
from common.date import ENGLISH_MONTH
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
ENGLISH_MONTH = common.date.ENGLISH_MONTH

#Author:陈卓玮
# check: 凌敏 pass
# debug: 修复问题 注：有几个页面确实只有一张图片或者是一份pdf文件链接
#网站新闻量少



class aei_edu_news(BaseSpider):
    name = 'aei_edu'
    website_id = 707
    language_id = 2037
    start_urls = ['https://aei.um.edu.my/latest-news','https://aei.um.edu.my/latest-events',
                  'https://aei.um.edu.my/events-in-2021','https://aei.um.edu.my/events-in-2020',
                  'https://aei.um.edu.my/news-archive-2021']

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'lxml')

        for i in soup.select('.course-item'):
            title = (i.select_one('.course-title a').text)
            url = (i.select_one('.course-title a').get('href'))
            if 'https' not in url:
                url = "https://aei.um.edu.my/" + url
            eng_time = (i.select_one('.course-seats').text.strip().split(' '))
            eng_time[0], eng_time[2] = eng_time[2], eng_time[0]
            eng_time[1] = str(ENGLISH_MONTH[eng_time[1]])
            eng_time = '-'.join(eng_time)
            meta={'title':title,'time':eng_time+' 00:00:00'}
            time_stamp = utils.date_util.DateUtil.formate_time2time_stamp(eng_time+' 00:00:00')
            if self.time == None or time_stamp >= self.time:
                yield Request(url=url,callback=self.essay_parser,meta=meta)

    def essay_parser(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        body=''
        for i in soup.select("p"):
            body+=i.text.replace('\n','')+'\n'
        body = html.escape(body)

        img=[]
        try:
            for i in soup.select('img'):
              img.append("https://aei.um.edu.my/" +i.get('src'))
        except:
            pass

        abstract = body.split('\n')[0]
        for i in body.split('\n'):
            if i != '\n' and i !='':
                abstract=i
                break

        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = 'News&Events'
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = response.meta['time']
        item['images'] = img
        yield item



