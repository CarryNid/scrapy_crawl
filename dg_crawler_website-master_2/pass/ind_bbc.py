# encoding: utf-8
import requests
import scrapy
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import re
import common.date as date

# author:凌敏
class ind_bbcSpider(BaseSpider):
    name = 'ind_bbc'
    website_id = 385
    language_id = 1952
    start_urls = ['http://www.bbc.com/indonesia']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('ul', class_='bbc-11krpir e1ibkbh74').find_all('li')[1:4]:
            cate_url = 'https://www.bbc.com'+i.find('a').get('href')
            category1 = i.find('a').text
            meta = {'category1': category1}
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('ul', class_='bbc-1kz5jpr euuxl8v2').find_all('li'):
            images = i.find('img').get('src')
            content_url = i.find('h2', class_='bbc-o8gkn0 ewr0zp70').find('a').get('href')
            title = i.find('h2', class_='bbc-o8gkn0 ewr0zp70').find('a').text
            pub_time = i.find('time').get('datetime')+' 00:00:00'
            last_time = pub_time
            meta = {'images': images,
                    'title': title,
                    'pub_time': pub_time,
                    'category1': response.meta['category1']}
            yield scrapy.Request(url=content_url, callback=self.parse3, meta=meta)
        if '?page' in response.url:
            turn_page = response.url.split('?page')[0]+soup.find('nav', class_='bbc-g1ov4l e19602dz5').find_all('span', class_='bbc-3ykijd e19602dz2')[-1].find('a').get('href')
        else:
            turn_page = response.url+soup.find('nav', class_='bbc-g1ov4l e19602dz5').find_all('span', class_='bbc-3ykijd e19602dz2')[-1].find('a').get('href')
        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)


    def parse3(self, response, **kwargs):
        item = NewsItem()
        item['body'] = ''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('main', role='main').find_all('div', class_='bbc-19j92fr essoxwk0'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('.')[0]
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item


