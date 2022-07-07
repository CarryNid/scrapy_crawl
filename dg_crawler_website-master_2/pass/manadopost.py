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
class manadopostSpider(BaseSpider):
    name = 'manadopost'
    website_id = 52
    language_id = 1952
    start_urls = ['http://www.manadopost.co.id/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find("div",class_="posts-grid two-columns").find_all("article"):
            title = i.find("h2",class_="entry-title").find("a").text
            abstract = i.find("div",class_='entry-summary').find("p").text
            last_time = i.find("div",class_='entry-meta').find("time",class_='entry-date published').get('datetime').split('T')[0]+" 00:00:00"
            url = i.find('span',class_='more-link-wrapper').find('a').get('href')
            meta={
                'title':i.find("h2",class_="entry-title").find("a").text,
                'abstract':i.find("div",class_='entry-summary').find("p").text,
                'pub_time':i.find("div",class_='entry-meta').find("time",class_='entry-date published').get('datetime').split('T')[0]+" 00:00:00"
            }
            yield scrapy.Request(url, callback=self.parse2, meta=meta)
        turn_page = soup.find('a',class_='next page-numbers').get('href')
        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse)

    def parse2(self,response):
        item = NewsItem()
        item['body']=''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.select('div.entry-content > p'):
            item['body'] += i.text
        item['images'] = [soup.find('div',class_="entry-content").find('img').get('src')]
        item['abstract'] = response.meta['abstract']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = ''
        item['category2'] = ''
        yield item
