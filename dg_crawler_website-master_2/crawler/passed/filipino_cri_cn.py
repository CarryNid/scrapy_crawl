import socket

import common.date
from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from utils import date_util

from datetime import datetime
import time
import re
import requests

global null
null = ''


# author:魏芃枫


class Filipino(BaseSpider):
    name = 'filipino_cri_cn'
    start_urls = ['http://filipino.cri.cn/balita.html']
    website_id = 1912  # 网站的id(必填)
    language_id = 1880  # 所用语言的id
    is_http = 1

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(response.text, "html.parser")
        category1 = soup.select('.card-c-nav a')
        more_href = soup.select('.more-b a')
        for i in range(1, len(more_href) + 1):
            if i == 4:
                meta1 = {'category1': 'Unknown'}
            else:
                meta1 = {'category1': category1[i - 1].text}  # 国家标题 共三个Tsina Daigdig ASEAN 第四个未知但存在
            href = "http://filipino.cri.cn"+more_href[i - 1].get('href')
            yield Request(href, callback=self.parse_pagelist, meta=meta1)

    def parse_pagelist(self, response):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(response.text, 'html.parser')
        pagedata = soup.find(attrs={'class': 'list-box txt-listUl'}).select_one('ul').get('pagedata')
        pagedata_dict = eval(pagedata)
        total_page = pagedata_dict["total"]
        urls = pagedata_dict["urls"]
        for i in range(0, total_page):
            url = urls[i]
            yield Request("http://filipino.cri.cn"+url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find(attrs={'class': 'list-box txt-listUl'}).select('ul li h4')
        for i in articles:
            pub_time = i.select_one('i').text
            timestamp = date_util.DateUtil.formate_time2time_stamp(pub_time)
            try:
                if self.time == None or timestamp >= int(self.time):
                    href = i.select_one('a').get('href')
                    title = i.select_one('a').text
                    meta1 = response.meta  # 含category1
                    meta2 = {'title': title, 'pub_time': pub_time}
                    meta2.update(meta1)
                    yield Request("http://filipino.cri.cn"+href, callback=self.parse_detail, meta=meta2)
                else:
                    self.logger.info('时间截止！')
            except:
                continue

    def parse_detail(self, response):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select_one('#abody') is not None:
            body = soup.select_one('#abody').text
        else:
            body = soup.select_one('.cn-abody-inner').text
        item = NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['abstract'] = item['body'].split('\n')[0]
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['images'] = None
        return item
