# encoding: utf-8
import time

from bs4 import BeautifulSoup
from utils.util_old import Util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

#Auther: 贺佳伊
class DemoSpiderSpider(BaseSpider):
    name = 'newswalla'
    website_id = 1025
    language_id = 1926
    start_urls = ['https://news.walla.co.il/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        news_page_url = 'https://news.walla.co.il/archive/1?year=2021'
        response.meta['category1'] =soup.select_one('#root > div > header.no-mobile-app.css-1huua83.main-header > nav.css-15d53xb > div > ul.vertical-menu > li:nth-child(5) > a').text
        yield Request(url=news_page_url,callback=self.parse_year,meta=response.meta)

    def parse_year(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        s = soup.select(
            '#root > div > section.walla-core-container.css-11x5rb1.css-1nwbluu > section > main > section > div > div > a')
        for i in s:
            response.meta['category2'] = i.text
            news_page_url = 'https://news.walla.co.il' + i.get('href')
            response.meta['page'] = 1
            response.meta['url'] = news_page_url
            yield Request(url=news_page_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self,response):
        time.sleep(3)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select('#root > div > section.walla-core-container.css-11x5rb1.css-1nwbluu > section > main > section > div > ul > li ')
        for i in a:
            t = i.select_one('a > article > div > footer > div.pub-date').text
            if (len(t) == 24):
                pub_time = t[20:24] + '-' + t[17:19] + '-' + t[14:16] + ' ' + t[8:13] + ':00'
            else:
                t0 = t.split('/')
                pub_time = t0[2] + '-' + t0[1].rjust(2, '0') + '-' + t0[0][6:].rjust(2, '0') + ' ' + t0[0][:5] + ':00'
        if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(pub_time):
             for i in a:
                news_url = i.select_one('a').get('href')
                response.meta['title'] = i.select_one('a > article > div > h3').text
                t = i.select_one('a > article > div > footer > div.pub-date').text
                if (len(t) == 24):
                    response.meta['time'] = t[20:24] + '-' + t[17:19] + '-' + t[14:16] + ' ' + t[8:13] + ':00'
                else:
                    t0 = t.split('/')
                    response.meta['time'] = t0[2] + '-' + t0[1].rjust(2, '0') + '-' + t0[0][6:].rjust(2, '0') + ' ' + t0[0][:5] + ':00'
                response.meta['abstract'] = i.select_one(' a > article > div > p').text
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            response.meta['page'] = response.meta['page'] + 1
            try:
                next_page_url = self.start_urls +'&page=' +str(response.meta['page'])
                yield Request(url=next_page_url, callback=self.parse_page,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['body'] = soup.select_one('#root > div > section > section > section > main > div > article > section > section').text
        item['abstract'] = response.meta['abstract']
        try:
            a = soup.select_one(
                '#root > div > section > section > section > main > div > article > section.item-main-content > section > section > div > figure >picture >img').get(
                'srcset')
            pic = []
            pics = a.split()
            for i in pics:
                if (i[0] == 'h'):
                    pic.append(i)
        except:
            pic = None
        item['images'] = pic
        yield item