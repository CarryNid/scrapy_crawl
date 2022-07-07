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
Português_simple_month={
    'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04', 'Mai': '05', 'Jun': '06',
    'Jul': '07', 'Ago': '08', 'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
}

class hojemacauSpider(BaseSpider):
    name = 'hojemacau'
    website_id = 671
    language_id = 2122
    start_urls = ['https://hojemacau.com.mo']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('ul', id='primary-menu').find_all('li'):
            category1 = i.text
            cate_url = i.find('a').get('href')
            meta1 = {
                'category1': category1
            }
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('main', id='primary').find_all('article'):
            title = i.find('header', class_='entry-header').find('h2', class_='entry-title').find('a').text
            content_url = i.find('header', class_='entry-header').find('h2', class_='entry-title').find('a').get('href')
            if i.find('a', class_='post-thumbnail') is not None:
                if i.find('a', class_='post-thumbnail').find('img') is not None:
                    images = i.find('a', class_='post-thumbnail').find('img').get('src')
                else:
                    images = []
            else:
                images = []
            ptime = i.find('footer', class_='entry-footer').text.strip('\n').strip('\t')
            t = ptime.split(' ')
            year = t[2]
            month = Português_simple_month[t[1]]
            day = t[0]
            time = year + '-' + month + '-' + day + ' 00:00:00'
            last_time = time
            meta = {
                'title': title,
                'images': images,
                'pub_time': time,
                'category1': response.meta['category1']
            }
            yield scrapy.Request(content_url, callback=self.parse3, meta=meta)
        if soup.find('div', class_='navigation_new').find('ol', class_='wp-paginate wpp-modern-grey font-inherit') is not None:
            page_url = soup.find('div', class_='navigation_new').find('ol', class_='wp-paginate wpp-modern-grey font-inherit').find_all('li')[-1].find('a').get('href')
            if self.time is not None:
                if self.time < DateUtil.formate_time2time_stamp(last_time):
                    yield scrapy.Request(url=page_url, callback=self.parse2, meta=response.meta)
                else:
                    self.logger.info("时间截止")
            else:
                yield scrapy.Request(url=page_url, callback=self.parse2, meta=response.meta)

    def parse3(self, response, **kwargs):
        item = NewsItem()
        item['body'] = ''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('div', class_='entry-content').find_all('p'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('.')[0]
        item['images'] = [response.meta['images']]
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item

