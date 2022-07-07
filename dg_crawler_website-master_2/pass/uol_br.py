# encoding: utf-8
import json

import requests
from bs4 import BeautifulSoup
import utils.date_util
import common.date
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

#Author:陈卓玮
class uol_br(BaseSpider):
    name = 'uol_br'
    website_id = 2075
    language_id = 2122
    start_urls = ['https://noticias.uol.com.br/ultimas/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text)
        for i in soup.select('.flex-wrap > div'):
            try:
                essay_url = (i.select_one('a').get('href'))
                essay_title = (i.select_one('h3').text)
                essay_time = (i.select_one('time').text).split(' ')[0].split('/')[2]+"-"+(i.select_one('time').text).split(' ')[0].split('/')[1]+"-"+(i.select_one('time').text).split(' ')[0].split('/')[0]+" 00:00:00"
                meta = {'essay_title':essay_title,'essay_time':essay_time}
                if 'video' not in essay_url:
                    yield Request(url = essay_url,meta = meta,callback=self.essay_content_parser)
            except:
                pass

        time_stamp = utils.date_util.DateUtil.formate_time2time_stamp(essay_time)
        if self.time == None or self.time <= time_stamp:
            try:
                yield Request(url="https://www.uol.com.br/eleicoes/service/?loadComponent=results-index&data=" + soup.select_one('button').get('data-request'))
            except:
                pass

    def essay_content_parser(self,response):
        soup = BeautifulSoup(response.text)
        img = []
        content=''
        for i in soup.select('p'):
            content+=i.text.strip()+'\n'
        for i in soup.select('img'):
            img.append(i.get('src'))

        item = NewsItem()
        item['title'] = response.meta['essay_title']
        item['category1'] = 'news'
        item['body'] = content
        item['abstract'] = content.split('\n')[0]
        item['pub_time'] = response.meta['essay_time']
        item['images'] = img
        yield item

