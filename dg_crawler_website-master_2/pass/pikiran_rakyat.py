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
india_month={
    'Januari':'01', 'Februari':'02', 'Maret':'03', 'April':'04', 'Mei':'05', 'Juni':'06',
    'Juli':'07', 'Agustus':'08', 'September':'09', 'Oktober':'10','November':'11','Desember':'12'
}
class pikiran_rakyatSpider(BaseSpider):
    name = 'pikiran_rakyat'
    website_id = 55
    language_id = 1952
    start_urls = ['http://www.pikiran-rakyat.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.select('nav.nav > ul.nav__wrap > li > a'):
            meta1={'category1': i.text}
            cate_url = i.get('href')
            yield scrapy.Request(url=cate_url,callback=self.parse2,meta=meta1)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time=''
        category1 = response.meta['category1']
        for i in soup.find('section', class_='latest mt3 clearfix').find_all('div', class_='latest__item'):
            if i.find('h4', class_='latest__subtitle').find('a').text == category1:
                category2 = ''
            else:
                category2 = i.find('h4', class_='latest__subtitle').find('a').text
            time = i.find('date', class_='latest__date').text.split(',')[0].split(' ')
            year = time[2]
            month = india_month[time[1]]
            day = time[0]
            if int(day) < 10:
                day = '0' + day
            last_time = year+'-'+month+'-'+day+' 00:00:00'
            if i.find('div', class_='latest__img') is not None:
                images = i.find('div', class_='latest__img').find('img').get('data-src')
            else:
                images = []
            meta = {
                'title': i.find('h2', class_='latest__title').find('a').text,
                'images': images,
                'pub_time': year+'-'+month+'-'+day+' 00:00:00',
                'category1': category1,
                'category2': category2
            }
            url = i.find('h2', class_='latest__title').find('a').get('href')
            yield scrapy.Request(url,callback=self.parse3,meta=meta)
        if soup.find('a', rel='next') is not None:
            turn_page = soup.find('a', rel='next').get('href')
            if self.time is not None:
                if self.time < DateUtil.formate_time2time_stamp(last_time):
                    yield scrapy.Request(url=turn_page, callback=self.parse2,meta=response.meta)
                else:
                    self.logger.info("时间截止")
            else:
                yield scrapy.Request(url=turn_page, callback=self.parse2,meta=response.meta)


    def parse3(self, response, **kwargs):
        item = NewsItem()
        item['body'] =''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('article',class_='read__content clearfix').find_all('p'):
            item['body'] += i.text
        if soup.find('div', class_='paging__all') is not None:
            body2 = self.parse4(soup.find('div', class_='paging__all').find('a').get('href'))
            item['body'] += body2
        for i in soup.find('article', class_='read__content clearfix').find_all('p'):
            if len(i.text.split('.')[0]) > 2:
                item['abstract'] = i.text.split('.')[0]
                break
            else:
                continue
        item['images'] = [response.meta['images']]
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        yield item

    @staticmethod
    def parse4(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        body = ''
        for i in soup.find('article',class_='read__content clearfix').find_all('p'):
            body += i.text
        return body