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
class klik_galamediaSpider(BaseSpider):
    name = 'klik_galamedia'
    website_id = 50
    language_id = 1952
    start_urls = ['http://www.klik-galamedia.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find("div",id="content").find_all("article"):
            title = i.find('a').text
            if i.find("div",class_="entry-content").find("p").find('strong') is not None:
                abstract = i.find("div",class_="entry-content").find("p").find("strong").text
            else:
                abstract = i.find("div", class_="entry-content").find("p").text
            body=''
            for a in i.find("div",class_="entry-content").find_all('p')[1:]:
                body += a.text
            last_time = i.find("footer",class_="entry-meta").find("time",class_="entry-date").get("datetime").split('T')[0] + ' 00:00:00'
            meta={
                "title": i.find("header",class_="entry-header").find("h1",class_="entry-title").find("a").text,
                "abstract": abstract,
                "pub_time": i.find("footer",class_="entry-meta").find("time",class_="entry-date").get("datetime").split('T')[0] + ' 00:00:00',
                "body": body
            }
            item = NewsItem()
            item['body'] = meta['body']
            item['abstract'] = meta['abstract']
            item['title'] = meta['title']
            item['pub_time'] = meta['pub_time']
            item['category1'] = ''
            item['category2'] = ''
            item['images'] = []
            yield item
        global turn_page
        if soup.find("div", class_="nav-previous").find("a") is not None:
            turn_page = soup.find("div", class_="nav-previous").find("a").get("href")
        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse)



    # def parse2(self, response):
    #     item = NewsItem()
    #     # soup = BeautifulSoup(response.text, features='lxml')
    #     item['body'] += response.meta['body']
    #     item['abstract'] = response.meta['abstract']
    #     item['title'] = response.meta['title']
    #     item['pub_time'] = response.meta['pub_time']
    #     item['category1'] = ''
    #     item['category2'] = ''
    #     item['images'] = ''
    #     yield item
