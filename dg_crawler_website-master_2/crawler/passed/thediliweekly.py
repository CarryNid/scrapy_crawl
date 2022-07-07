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
Português_month={
    'Janeiro':'01', 'Fevereiro':'02', 'Março':'03', 'Abril':'04', 'Maio':'05', 'Junho':'06',
    'Julho':'07', 'Agosto':'08', 'Setembro':'09', 'Outubro':'10','Novembro':'11','Dezembro':'12'
}

class thediliweeklySpider(BaseSpider):
    name = 'thediliweekly'
    website_id = 370
    language_id = 2122
    start_urls = ['https://thediliweekly.com/tl/notisias']  # http://thediliweekly.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        category1 = soup.find('li', id='current').find('span').text.strip()
        for i in soup.find('ul', class_='menu level1').find_all('a', class_='orphan item'):
            category2 = i.find('span').text.strip()
            cate_url = 'https://thediliweekly.com' + i.get('href')
            meta1 = {
                'category1': category1,
                'category2': category2
            }
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find_all('div', class_='rt-article'):
            title = i.find('div', class_='article-header').find('a').text
            images = 'https://thediliweekly.com' + i.find('figure').find('img').get('src')
            time = i.find('dd', class_='rt-date-published').text.split(': ')[1].split(' ')
            year = time[2].strip()
            month = Português_month[time[1]]
            day = time[0]
            last_time = year+'-'+month+'-'+day+' 00:00:00'
            abstract = i.find('figcaption').text
            meta = {
                'title': title,
                'images': images,
                'pub_time': year+'-'+month+'-'+day+' 00:00:00',
                'abstract': abstract,
                'category1': response.meta['category1'],
                'category2': response.meta['category2']
            }
            content_url = 'https://thediliweekly.com' + i.find('a', class_='readon').get('href')
            yield scrapy.Request(content_url, callback=self.parse3, meta=meta)

        if soup.find('div', class_='pagination').find('li', class_='pagination-next').find('a') is not None:
            next_page_url = 'https://thediliweekly.com' + soup.find('div', class_='pagination').find('li', class_='pagination-next').find('a').get('href')
            if self.time is not None:
                if self.time < DateUtil.formate_time2time_stamp(last_time):
                    yield scrapy.Request(url=next_page_url, callback=self.parse2, meta=response.meta)
                else:
                    self.logger.info("时间截止")
            else:
                yield scrapy.Request(url=next_page_url, callback=self.parse2, meta=response.meta)


    def parse3(self, response, **kwargs):
        item = NewsItem()
        item['body'] = ''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('article', class_='item-page').find_all('p'):
            item['body'] += i.text
        item['images'] = [response.meta['images']]
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['abstract'] = response.meta['abstract']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        yield item


