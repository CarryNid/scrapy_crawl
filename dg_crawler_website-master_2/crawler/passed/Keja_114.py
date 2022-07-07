# encoding: utf-8
from bs4 import BeautifulSoup

import utils.date_util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import time

# Author:陈卓玮
class Keja_114(BaseSpider):
    name = 'Keja_114'
    website_id = 114
    language_id = 1952
    allowed_domains = ['kejaksaan.go.id']
    start_urls = ['http://www.kejaksaan.go.id/berita.php?idu=0&hal=1']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            maxpage = int(soup.select_one(' td > a:nth-child(7)').get('href').split('=')[-1])
        except:
            maxpage = 1796
        lists = soup.select('td')

        passages = []
        exist = 0
        t = ''
        global t_
        for i in lists:
            img = []
            try:
                ti = i.select_one('span.t_date').text.split('-')
                t = ti[2] + '-' + ti[1] + '-' + ti[0]
                title = i.select_one('span.t_berita > a.mn1').text
                detail_url = i.select_one('span.t_berita > a.mn1').get('href')
                abstract = i.select_one('span.teks').text
                img.append("https://www.kejaksaan.go.id/" + i.select_one('span.teks > img').get('src'))
                exist = 0
                for s in passages:
                    if s['title'] == title and t != None and title != None:
                        exist = 1
                if exist == 0:
                    passages.append(
                        {'time': t, 'title': title, 'url': detail_url, 'abstract': abstract, 'img': img, 'body': ''})
            except:
                 pass


        for p in passages:
            meta = {'content': p}
            if p['time']!=None:
                t_stamp =  utils.date_util.DateUtil.formate_time2time_stamp(p['time']+ ' 00:00:00')
                # print(p['time']+ '///'+str(t_stamp))

                if self.time == None or t_stamp >= self.time:
                    yield Request(url='http://www.kejaksaan.go.id' + p['url'], callback=self.detail_parser, meta=meta)

        this_page = int(response.url.split('hal=')[-1])
        next_page_url = 'http://www.kejaksaan.go.id/berita.php?idu=0&hal=' + str(this_page+1)
        if self.time == None or t_stamp >=self.time and this_page < maxpage:
            yield Request(url=next_page_url)

    def detail_parser(self, response):
        item = NewsItem()
        data = response.meta['content']
        soup = BeautifulSoup(response.text, 'html.parser')

        lists = soup.select(' tr > td > p')
        body = ''
        for i in lists:
            body = body + i.text + '\n'
        data['body'] = body

        imgs = soup.select(' tr > td > p > img')
        for img in imgs:
            data['img'].append("https://www.kejaksaan.go.id/" + img.get('src'))
        item['title'] = data['title']
        item['body'] = data['body']
        item['abstract'] = data['abstract']
        item['pub_time'] = data['time']
        item['images'] = data['img']
        item['category1'] = "Beranda"
        item['category2'] = "Berita"
        yield item






