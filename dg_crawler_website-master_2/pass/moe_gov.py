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
# 新闻无category, 部分文章body为空是因为内容全为图片
malay_month = {'Januari': '01', 'Februari': '02', 'Mac': '03', 'April':'04', 'Mei': '05', 'Jun': '06',
'Julai': '07', 'Ogos': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Disember': '12'}


class moe_govSpider(BaseSpider):
    name = 'moe_gov'
    website_id = 400
    language_id = 2036
    start_urls = ['https://www.moe.gov.my/menumedia/media-elektronik/berita-dan-aktiviti']  # http://www.moe.gov.my
    # is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('tbody').find_all('tr'):
            title = i.find('td', class_='list-title').find('a').text
            content_url = 'https://www.moe.gov.my' + i.find('td', class_='list-title').find('a').get('href')
            time = i.find('td', class_='list-date small').text.strip()
            year = time.split(' ')[2]
            month = malay_month[time.split(' ')[1]]
            day = time.split(' ')[0]
            pub_time = year + '-' + month + '-' + day + ' 00:00:00'
            meta = {'title': title,
                    'pub_time': pub_time}
            last_time = pub_time
            yield scrapy.Request(url=content_url, callback=self.parse2, meta=meta)
        turn_page = 'https://www.moe.gov.my' + soup.find('div', class_='pagination').find('ul').find_all('li')[-1].find(
            'a').get('href')
        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse)

    def parse2(self, response, **kwargs):
        item = NewsItem()
        item['body'] = ''
        item['images'] = []
        soup = BeautifulSoup(response.text, features='lxml')
        item['body'] = soup.find('div', class_='uk-margin-medium-top').text
        for i in soup.find('div', class_='uk-margin-medium-top').find_all('img'):
            item['images'].append('https://www.moe.gov.my' + i.get('src'))
        item['abstract'] = item['body'].split('.')[0]
        item['category1'] = ''
        item['category2'] = ''
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        yield item

