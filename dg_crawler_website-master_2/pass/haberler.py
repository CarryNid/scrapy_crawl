# -*- coding = utf-8 -*-
# @Time : 5:21 下午
# @Author : 阿童木
# @File : haberler.py
# @software: PyCharm



from bs4 import BeautifulSoup as mutong
import re
from scrapy import Request
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil

#author:李沐潼

class haberlerSpider(BaseSpider):
    name = 'haberler'
    website_id = 1814
    language_id = 2227
    start_urls = ['https://www.haberler.com/magazin/']

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta = {'category1': 'Magazin Haberleri'}
        category=soup.select('.hbftcolContent>.hbftCol>a')
        for item in category:
            meta['category2']=item.get('title')
            yield Request(item.get('href'),meta=meta,callback=self.parse_news)

    def parse_news(self, response):
        soup = mutong(response.text, 'html.parser')
        news=soup.select('.p12-col>a')
        for item in news:
            url='https://www.haberler.com'+item.get('href')
            yield Request(url, meta=response.meta, callback=self.parse_items)
    def parse_items(self,response):
        soup=mutong(response.text,'html.parser')
        t_a=soup.select('time')
        #print(t_a)
        if t_a!=[]:
            t = t_a[0].get('datetime')
            tt = t.split('T')
            t_formal = tt[0] + ' ' + tt[1][:8]
         #   print(t_formal)

            if self.time is None or DateUtil.formate_time2time_stamp(t_formal) >= int(self.time):
                item = NewsItem()
                item['title'] = soup.select('header>h1')

                item['category1'] = response.meta['category1']
                item['category2'] = response.meta['category2']
                item['body'] = ' '.join([i.text for i in soup.select('main>p')])
                item['abstract'] = soup.select('header>h2')
                item['pub_time'] = t_formal
                if soup.select('img') !=[]:
                    item['images'] =soup.select('img')[0].get('data-src')
                else:
                    item['images']=None
                    #print(soup.select('img'))
                yield item
            else:
                return

