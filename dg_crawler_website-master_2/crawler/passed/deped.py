# encoding: utf-8
from bs4 import BeautifulSoup
from utils.util_old import Util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author :钟钧仰
class DepedSpiderSpider(BaseSpider):
    name = 'deped'
    website_id = 1255
    language_id = 1866
    start_urls = ['https://www.deped.gov.ph/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        menu1 = soup.select('#main-nav > div > div > nav > ul > li')[5].select("li")[2].select('li')
        for i in menu1:
            if i.text != 'Videos':
                news_page = i.select_one('a').get('href')
                response.meta['category1'] = i.text
                yield Request(url=news_page, callback=self.parse_page, meta=response.meta)
        news_page3 = 'https://www.deped.gov.ph/category/issuances/deped-orders/'
        response.meta['category1'] = 'DepEd Orders'
        yield Request(url=news_page3, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):  # 新闻所在页面
        soup = BeautifulSoup(response.text, 'lxml')
        news_page = soup.select('#content > div')
        flag = True
        last_time=''
        for i in news_page:
            url = i.select_one('header > h2 > a').get('href')
            t = url.split('/')
            response.meta['time'] = t[3] + '-' + t[4] + '-' + t[5] + " 00:00:00"
            response.meta['title'] = i.select_one('header > h2 > a').text
            response.meta['abstract'] = i.select_one('div > div >p').text
            last_time=response.meta['time']
            yield Request(url=url, callback=self.parse_item, meta=response.meta)
        if int(self.time) >= DateUtil.formate_time2time_stamp(last_time):
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page = soup.select_one('#nav-below > div > a').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['pub_time'] = response.meta['time']
        item['abstract'] = response.meta['abstract']
        image_number = soup.select('#main-content >div >div >article >div >table >thead >tr >td >div >div >div >ul >li')
        if len(image_number) > 1:
            images = []
            for i in image_number:
                images.append(i.select_one('a').get('href'))
            item['images'] = images
        else:
            try:
                item['images'] = soup.select_one('#main-content >div >div >article >div >table >thead >tr >td >img ').get('src')
            except:
                try:
                    item['images'] = soup.select_one('#main-content >div >div >article >div >table >thead >tr >td >a >img ').get('src')
                except:item['images'] =''
        all_p = soup.select('#main-content >div >div >article >div >p ')
        p_list = []
        for i in all_p:
            try:
                p_list.append(i.text)
            except:
                continue
        item['body'] = '\n'.join(p_list)
        yield item
