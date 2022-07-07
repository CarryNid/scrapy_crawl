# -*- coding = utf-8 -*-
# @Time : 3:54 下午
# @Author : 阿童木
# @File : buzzfeed.py
# @software: PyCharm
from bs4 import BeautifulSoup as mutong
import re
from scrapy import Request
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import requests
from bs4 import BeautifulSoup as mutong


class buzzfeedSpider(BaseSpider):
    i=0
    j=1
    name = 'buzzfeed'
    website_id = 1781
    language_id = 1866
    start_urls = ['https://www.buzzfeednews.com']


#aurhor：李沐潼


    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        iii = [
            'https://www.buzzfeednews.com/us/feed/section/arts-entertainment?page=',
            'https://www.buzzfeednews.com/us/feed/section/books?page=',
            'https://www.buzzfeednews.com/us/feed/section/celebrity?page=',
            'https://www.buzzfeednews.com/us/feed/section/culture?page=',

            'https://www.buzzfeednews.com/us/feed/section/health?page=',
            'https://www.buzzfeednews.com/us/feed/section/inequality?page=',
            'https://www.buzzfeednews.com/investigations',
            'https://www.buzzfeednews.com/us/feed/section/jpg?page=',

            'https://www.buzzfeednews.com/us/feed/section/lgbtq?page=',
            'https://www.buzzfeednews.com/us/feed/collection/opinion?page=',
            'https://www.buzzfeednews.com/us/feed/section/politics?page=',
            'https://www.buzzfeednews.com/us/feed/section/science?page=',

            'https://www.buzzfeednews.com/us/feed/section/tech?page=',
            'https://www.buzzfeednews.com/us/feed/section/world?page='
            ]
        category1s = soup.select('.newsblock-page-footer__internal>nav>.newsblock-page-footer__list>li>a')
        for category1 in category1s:
            response.meta['category1'] = category1.text
            if self.i <14:
                while True:
                    url=iii[self.i]+str(self.j)
                    self.j+=1
                    if requests.get(url).status_code!=404:
                        yield Request(url, meta=response.meta, callback=self.parse_section)
                    else:
                        break
            self.i+=1



    def parse_section(self,response):
        soup = mutong(response.text, 'html.parser')
        urls= soup.select('h2>a')
        for new_url in urls:
           yield Request(new_url.get('href'),meta=response.meta,callback=self.parse_items)

    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        if soup.select('time') !=[]:
            ll= soup.select('time')[0].get('datetime')
            if ll is not None:
                li=ll.split('T')
                ti = li[0] + ' ' + li[1][:8]
            else:
                ti=DateUtil.time_now_formate()
        else:
            ti=DateUtil.time_now_formate()
        if self.time is None or DateUtil.formate_time2time_stamp(ti) >= int(self.time):
            item = NewsItem()
            title1 = soup.select('.headline_container__AwL7p >h1')
            title2 = soup.select('.news-article-header__title')
            if title1 == []:
                item['title'] = title2[0].text
            else:
                item['title'] = title1[0].text

            test1 = soup.select('.headline_container__AwL7p >p')
            test2 = soup.select('.news-article-header__dek')
            if test1 == []:
                item['abstract'] = test2[0].text
            else:
                item['abstract'] = test1[0].text

            item['category1'] = response.meta['category1']
            item['category2'] = None
            body_pre=[i.text for i in soup.select('.subbuzz__description >p')]
            if body_pre!=[]:
                item['body'] = ''.join(body_pre)
            else:
                item['body']=item['abstract']


            item['pub_time'] = ti
            img_list=[]
            for i in soup.select('img'):
                if 'data' not in i.get('src'):
                    img_list.append(i.get('src'))

            item['images'] = img_list
            yield item
        else:
            return