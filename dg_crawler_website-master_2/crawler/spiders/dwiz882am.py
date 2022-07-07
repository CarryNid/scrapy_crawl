import socket

import common.date
import utils.date_util
from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from utils import date_util
from scrapy.http import FormRequest

from datetime import datetime
import time
import re
import requests

global null
null = ''


# author:魏芃枫


class Dwiz882am(BaseSpider):
    name = 'dwiz882am'
    start_urls = ['https://www.dwiz882am.com/']
    website_id = 1914  # 网站的id(必填)
    language_id = 1880  # 所用语言的id
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        category1_list = soup.select('.theiaStickySidebar .inner-arrow a')
        for i in category1_list:
            category1 = i.text
            meta1 = {'category1': category1}
            category1_href = i.get('href')
            yield Request(category1_href, callback=self.parse_pages, meta=meta1)

    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        title_list = soup.select('h2 a')
        for i in title_list:
            e_time = soup.select_one('.penci-box-meta span').text
            year = e_time.split(',')[1].strip()
            month_day = e_time.split(',')[0]
            month = month_day.split(' ')[0]
            day = month_day.split(' ')[1]
            pub_time = year + '-' + str(common.date.ENGLISH_MONTH[month]) + '-' + day + ' 00:00:00'
            timestamp = utils.date_util.DateUtil.formate_time2time_stamp(pub_time)
            try:
                if self.time == None or timestamp >= int(self.time):
                    href = i.get('href')
                    meta2 = {'pub_time': pub_time}
                    meta2.update(response.meta)
                    yield Request(href, callback=self.parse_article, meta=meta2)
                else:
                    self.logger.info('时间截止！')
            except:
                continue
        # 查找下一页URL 该网站只能通过点击下一页而不能点击页数
        try:
            nextpage_url = soup.select_one(".older a").get('href')
            yield Request(nextpage_url, callback=self.parse_pages,meta=response.meta)
        except:
            self.logger.info("No more pages")



    def parse_article(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        image_flag = 1
        try:
            src = soup.select_one('.post-image a img').get('src')
        except:
            image_flag = 0

        title = soup.select_one('h1').text
        paragraphs = soup.select('.post-entry p')
        abstract = paragraphs[0].text
        body = ''
        for i in paragraphs[0:-1]:
            body += i.text

        item = NewsItem()
        item['title'] = title
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['abstract'] = abstract
        item['category1'] = response.meta['category1']
        item['category2'] = None
        if image_flag == 1:
            item['images'] = src
        else:
            item['images'] = None
        yield item
