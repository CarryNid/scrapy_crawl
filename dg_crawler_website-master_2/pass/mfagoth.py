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
Thai_month = {'ม.ค.': '01', 'ก.พ.': '02', 'มี.ค.': '03', 'เม.ย.': '04', 'พ.ค.': '05', 'มิ.ย.': '06', 'ก.ค.': '07',
              'ส.ค.': '08', 'ก.ย.': '09', 'ต.ค.': '10', 'พ.ย.': '11', 'ธ.ค.': '12'}

DAY = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06', '7': '07', '8': '08', '9': '09'}

class mfaSpider(BaseSpider):
    name = 'mfa'
    website_id = 1608
    language_id = 2208
    start_urls = ['https://www.mfa.go.th/th/page/%E0%B8%82%E0%B9%88%E0%B8%B2%E0%B8%A7%E0%B9%80%E0%B8%94%E0%B9%88%E0%B8%99?menu=5d5bd3d815e39c306002aac4&p=1']  # http://www.mfa.go.th/
    # is_http = 1
    # proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('div', class_='LeftSidestyled__LeftSideWrapper-sc-engdnh-1 qDPVD my-3 page-leftside').find_all('ul', class_='nav flex-column')[5:10]:
            category1 = i.find('li').find('a').text
            cate_url = 'https://www.mfa.go.th' + i.find('li').find('a').get('href') + '&p=1'
            meta = {'category1': category1}
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        if soup.find('div', class_='content-width2').find('div', class_='px-3 row') is None:
            for i in soup.find('div', class_='content-width2').find('div', class_='row').find_all('div', class_='p-3 col-md-4'):
                title = i.find('div', class_='jsx-2368373130 content px-0 py-3 d-flex flex-column justify-content-between').find('a').find('div').get('title')
                content_url = 'https://www.mfa.go.th' + i.find('div', class_='jsx-2368373130 content px-0 py-3 d-flex flex-column justify-content-between').find('a').get('href')
                time = i.find('p', class_='date').text
                year = str(int(time.split(' ')[2])-543)
                month = Thai_month[time.split(' ')[1]]
                day = time.split(' ')[0]
                if int(day) < 10:
                    day = DAY[time.split(' ')[0]]
                pub_time = year+'-'+month+'-'+day+' 00:00:00'
                last_time = pub_time
                meta = {'title': title,
                        'pub_time': pub_time,
                        'category1': response.meta['category1']}
                yield scrapy.Request(url=content_url, callback=self.parse3, meta=meta)
        else:
            for i in soup.find('div', class_='content-width2').find('div', class_='px-3 row').find_all('div', class_='col-md-12'):
                title = i.find('div', class_='WrapTextstyled__WrapText-sc-1clzrix-0 cHHTGu ContentListstyled__Title-sc-1x5vi1m-1 idhQew col ml-4').get('title')
                content_url = 'https://www.mfa.go.th' + i.find('div', class_='pt-1 col-md-3').find_all('div', class_='row')[1].find('a').get('href')
                time = i.find('p', class_='date').text
                year = str(int(time.split(' ')[2])-543)
                month = Thai_month[time.split(' ')[1]]
                day = time.split(' ')[0]
                if int(day) < 10:
                    day = DAY[time.split(' ')[0]]
                pub_time = year+'-'+month+'-'+day+' 00:00:00'
                last_time = pub_time
                meta = {'title': title,
                        'pub_time': pub_time,
                        'category1': response.meta['category1']}
                yield scrapy.Request(url=content_url, callback=self.parse3, meta=meta)
        turn_page = response.url.split('&p=')[0]+'&p='+str(int(response.url.split('&p=')[1])+1)
        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)

    def parse3(self, response, **kwargs):
        item = NewsItem()
        item['images'] = []
        soup = BeautifulSoup(response.text, features='lxml')
        item['body'] = soup.find('div', class_='ContentDetailstyled__ContentDescription-sc-150bmwg-4 jWrYsI mb-3').text
        item['abstract'] = item['body'].split('.')[0]
        if soup.find('span', class_=' lazy-load-image-background blur lazy-load-image-loaded') is not None:
            for i in soup.find_all('span', class_=' lazy-load-image-background blur lazy-load-image-loaded'):
                item['images'].append(i.find('img').get('src'))
        else:
            item['images'] = []
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        yield item

