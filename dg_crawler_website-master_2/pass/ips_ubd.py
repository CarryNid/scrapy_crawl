# encoding: utf-8
from bs4 import BeautifulSoup

import utils.date_util
from common.date import ENGLISH_MONTH
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# Author:陈卓玮
class ips_ubd_spider(BaseSpider):
    name = 'ips_ubd_spider'
    website_id = 702
    language_id = 2036
    start_urls = ['https://ips.ubd.edu.bn/']

    def parse(self, response):
        cols = ['about-ips/','programmes/','category/news/','category/seminar-series/']

        yield Request(url = self.start_urls[0]+cols[0],callback=self.about_parse)
        yield Request(url = self.start_urls[0]+cols[1],callback=self.programs_parse)
        yield Request(url = self.start_urls[0]+cols[2],callback=self.news_parse)
        yield Request(url = self.start_urls[0]+cols[3],callback=self.news_parse)

    def about_parse(self,response):
        item = NewsItem()
        item['category1'] = 'About'

        soup = BeautifulSoup(response.text,'html.parser')
        title = soup.select_one('h2').text
        body = soup.select_one('div.entry-content').text
        abstract = body.split('\n')[2]
        imgs = []
        imgs.append(soup.select_one('img').get('src'))

        item['pub_time'] = '2022-01-21'
        item['images'] = imgs
        item['body'] = body
        item['abstract'] = abstract
        item['title'] = title
        yield item

    def programs_parse(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        for a in soup.select('article'):
            yield Request(url = a.select_one('a').get('href'),callback = self.programs_detail_parse)

    def programs_detail_parse(self,response):
        item = NewsItem()
        soup = BeautifulSoup(response.text,'html.parser')
        title = soup.select_one('h1').text
        category1 = 'programmes'
        abstract = soup.select_one('.programme-overview-info').text
        for i in soup.select('div.entry-content > div > div > div'):
            category2 = i.get('data-label')
            body = i.text
            pub_time = '2022-01-21'
            imgs=[]
            imgs.append(soup.select_one('img').get('src'))

            item['category1'] = category1
            item['category2'] = category2
            item['pub_time'] = pub_time
            item['images'] = imgs
            item['body'] = body
            item['abstract'] = abstract
            item['title'] = title
            yield item

    def news_parse(self,response):
        soup = BeautifulSoup(response.text,'html.parser')

        for a in soup.select('article'):
            d_url = a.select_one('a').get('href')
            time = a.select_one('time').get('datetime').replace('T', ' ').split('+')[0]
            meta = {'time':time}
            yield Request(url = d_url,meta = meta,callback=self.news_detail_parse)

        if self.time == None or utils.date_util.DateUtil.formate_time2time_stamp(time) >= self.time:
            try:
                next_url = soup.select_one('.nav-next > a').get('href')
                yield Request(url = next_url,callback=self.news_parse)
            except:
                pass

    def news_detail_parse(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        imgs=[]

        for i in soup.select('img'):
            imgs.append('https://' + i.get('src').split('//')[1])

        title = soup.select_one('h1').text
        body = ''
        for i in soup.select('.entry-content > p'):
            body = body + i.text.replace('\n', '') + '\n'

        abstract = body.split('\n')[0]
        item['category1'] = 'news&events'
        item['category2'] = 'news&seminars'
        item['pub_time'] = response.meta['time']
        item['images'] = imgs
        item['body'] = body
        item['abstract'] = abstract
        item['title'] = title
        yield item




















