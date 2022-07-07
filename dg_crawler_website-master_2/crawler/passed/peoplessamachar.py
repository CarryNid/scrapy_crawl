# encoding: utf-8
import requests
import scrapy
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import re
import common.date as date

# Sep 14, 2020
def time_adjust(past_time):
    month , day , year = past_time.split(' ')
    day = day.strip(',')
    if month == 'Jan':
        month = '01'
    elif month == 'Feb':
        month = '02'
    elif month == 'Mar':
        month = '03'
    elif month == 'Apr':
        month = '04'
    elif month == 'May':
        month = '05'
    elif month == 'Jun':
        month = '06'
    elif month == 'Jul':
        month = '07'
    elif month == 'Aug':
        month = '08'
    elif month == 'Sept':
        month =  '09'
    elif month == 'Oct':
        month = '10'
    elif month == 'Nov':
        month = '11'
    else:
        month = '12'
    if(int(day) < 10 ):
        day = '0' + day
    return year + '-' + month + '-' + day + ' 00:00:00'

# author:陈宣齐，2022.1.12
class peoplessamacharSpider(BaseSpider):
    name = 'peoplessamachar'
    website_id = 1146
    language_id = 1740
    start_urls = ['https://www.peoplessamachar.in/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find_all('div', class_='row')[2].select('div > ul')[0].select('ul > li > a'):
            yield scrapy.Request(url=i.get('href') , callback=self.parse2)

    def parse2(self,response):
        last_time = ''
        soup = BeautifulSoup(response.text , 'lxml')
        for i in soup.find('div', id='content').select('div div.post-item'):
            meta = {
                'pub_time':time_adjust(i.find('p',class_='post-meta').find('span').text),
                'title':i.find('h3').find('a').text,
                'img':i.find('img').get('data-src'),
                'category1':soup.find('h1',class_='page-title').text
            }
            last_time = i.find('p',class_='post-meta').find('span').text
            yield scrapy.Request(url=i.find('h3').find('a').get('href'),callback=self.parse3 , meta=meta)
        if soup.find('li',class_='next') is not None:
            if self.time is not None:
                if self.time > DateUtil.formate_time2time_stamp(time_adjust(last_time)):
                    yield scrapy.Request(url=soup.find('ul',class_='pagination').select('li.next  a')[0].get('href'),callback=self.parse2)
                else:
                    self.logger.info("超时了")
            else:
                yield scrapy.Request(url=soup.find('ul', class_='pagination').select('li.next  a')[0].get('href'),
                                     callback=self.parse2)

    def parse3(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['body'] = ''
        item['abstract'] = soup.find('div', class_='post-text').find('p').text
        for i in soup.find('div', class_='post-text').find_all('p'):
            item['body'] += i.text
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['images'] = [response.meta['img']]
        yield item