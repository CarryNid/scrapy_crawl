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

class portuguese_peopleSpider(BaseSpider):
    name = 'portuguese_people'
    website_id = 2072
    language_id = 2122
    start_urls = ['http://portuguese.people.com.cn/']
    is_http = 1
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('div', class_='w980 nav white clear').find_all('a')[1:-2]:
            cate_url = i.get('href')
            category1 = i.text
            meta1 = {
                'category1': category1,
                'cate_url': cate_url
            }
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)

    def get_time(self, url):
        response = requests.get(url, headers=self.header, timeout=(10, 15))
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find('div', class_='txt_time') is not None:
            t = soup.find('div', class_='txt_time').text.split('\xa0\xa0\xa0\xa0')[1].split(' ')[0].split('.')
        else:
            t = soup.find('div', class_='gqtxt_time clearfix').text.split('\xa0\xa0\xa0\xa0')[1].split(' ')[0].split('.')
        year = t[2]
        month = t[1]
        day = t[0]
        last_time = year + '-' + month + '-' + day + ' 00:00:00'
        return last_time


    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        content_url = ''
        for i in soup.find('div', class_='p1_1').find('ul', class_='p1_2').find_all('li'):
            if i.find('a').find('img') is not None:
                images = 'http://portuguese.people.com.cn' + i.find('a').find('img').get('src')
            else:
                images = []
            title = i.find('b').find('a').text
            abstract = i.find('p').text
            content_url = 'http://portuguese.people.com.cn' + i.find('b').find('a').get('href')
            meta = {
                'title': title,
                'images': images,
                'abstract': abstract,
                'category1': response.meta['category1']
            }
            yield scrapy.Request(content_url, callback=self.parse3, meta=meta)
        if soup.find('div', class_='page').find_all('a')[-1].get('href') is not None:
            add_url = response.meta['cate_url'].split('index')[0]
            page_url = add_url + soup.find('div', class_='page').find_all('a')[-1].get('href')
            last_time = self.get_time(content_url)
            if self.time is not None:
                if self.time < DateUtil.formate_time2time_stamp(last_time):
                    yield scrapy.Request(url=page_url, callback=self.parse2, meta=response.meta)
                else:
                    self.logger.info("时间截止")
            else:
                yield scrapy.Request(url=page_url, callback=self.parse2, meta=response.meta)

    def parse3(self, response, **kwargs):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find('div', class_='txt_time') is not None:
            t = soup.find('div', class_='txt_time').text.split('\xa0\xa0\xa0\xa0')[1].split(' ')[0].split('.')
        else:
            t = soup.find('div', class_='gqtxt_time clearfix').text.split('\xa0\xa0\xa0\xa0')[1].split(' ')[0].split('.')
        year = t[2]
        month = t[1]
        day = t[0]
        pub_time = year + '-' + month + '-' + day + ' 00:00:00'
        item['pub_time'] = pub_time
        item['body'] = ''
        if soup.find('div', class_='txt_con') is not None:
            for i in soup.find('div', class_='txt_con').find_all('p'):
                item['body'] += i.text.strip()
        else:
            for i in soup.find('div', class_='gqtxt_con').find_all('p'):
                item['body'] += i.text.strip()
        item['images'] = [response.meta['images']]
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        return item
