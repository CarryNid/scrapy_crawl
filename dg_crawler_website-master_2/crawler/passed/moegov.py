# -*- coding = utf-8 -*-
# @Time : 4:08 下午
# @Author : 阿童木
# @File : moegov.py
# @software: PyCharm
e_month={
        'January':'1',
        'February':2,
        'March':3,
        'April':4,
        'May':5,
        'June':6,
        'July':7,
        'August':8,
        'September':9,
        'October':10,
        'November':11,
        'December':12
}
#author:李沐潼
from bs4 import BeautifulSoup as mutong
import re
from scrapy import Request
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil


class moeSpider(BaseSpider):
    name = 'moegov'
    website_id = 1346
    language_id = 1797
    start_urls = ['http://www.moe.gov.mm/?q=news']
    is_http = 1


    def parse(self, response):
        soup=mutong(response.text,'html.parser')
        category1 = soup.select('section>h1')[0].text
        meta={'category1':category1}
        yield Request('http://www.moe.gov.mm/?q=news',meta=meta,callback=self.parse_page)

    def parse_page(self,response):
        flag= True
        soup = mutong(response.text, 'html.parser')
        new = soup.find_all(id='news-tbl')
        for item in new:
            date = item.find(id='news-date').text
            ti = re.split(r'\s*[,\s]\s*', date)
            tt = "{}-{}-{} {}:00".format(ti[3], e_month[ti[1]], ti[2], ti[-1])
            url = 'http://www.moe.gov.mm' + item.select('a')[0].get('href')
            tt_c=DateUtil.formate_time2time_stamp(tt)#转化为时间戳
            if self.time is None:
                response.meta['pub_time']=tt
                yield Request(url,meta=response.meta,callback=self.parse_items)
            else:
                if self.time<tt_c:
                    response.meta['pub_time']=tt
                    yield Request(url,meta=response.meta,callback=self.parse_items)
                else:
                    self.logger.info("时间截止")
                    flag=False
        if flag:
            try:
                next_url = 'http://www.moe.gov.mm' + soup.select('.pager>.pager-next>a')[0].get('href')
                yield Request(next_url,callback=self.parse_page,meta=response.meta)
            except:
                pass

    def parse_items(self,response):
        soup=mutong(response.text,'html.parser')
        item = NewsItem()
        item['title'] = soup.select('section>h1')[0].text
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = ' '.join([i.text for i in soup.select('p')])
        item['abstract'] = soup.select('p')[0].text
        item['pub_time'] = response.meta['pub_time']
        item['images'] = ' '.join([i.get('src') for i in soup.select('ul>li>a>img')])
        yield item
