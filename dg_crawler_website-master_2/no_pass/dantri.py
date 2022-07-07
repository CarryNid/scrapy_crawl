# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.items import *
from crawler.spiders import BaseSpider
from scrapy.http.request import Request
from utils.date_util import DateUtil
from copy import deepcopy
# author:hejiale


class DemoSpiderSpider(BaseSpider):
    name = 'dantri'
    website_id = 2046
    language_id = 1866
    start_urls = ['https://dantri.com.vn']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.col-840 .article .article-item .article-thumb'):
            yield Request(url='https://dantri.com.vn'+i.a.get('href'), callback=self.parse2)
        yield Request(url='https://dantri.com.vn' + soup.select(' .page-item')[-1].a.get('href'),callback=self.parse)

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select(' .author-time').text.strip().split(',')[1].split('-')[0].strip('/')
        time_ = ssd[-1] + '-' + ssd[-2] + '-' + ssd[0] + ' 00:00:00'
        meta={'pub_time_':time_}
        if self.time is None or DateUtil.formate_time2time_stamp(int(time_)) >= int(self.time):
            yield Request(url=response.url, callback=self.parse_item, meta=meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select_one(" .singular-container h1").text
        item['category1'] = 'ALL'
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select_one('.singular-content p')])
        item['abstract'] = soup.select_one(" .singular-container .singular-sapo").text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = [img.get('src') for img in soup.select('.singular-article .image img')]
        yield item