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
    name = 'debka'
    website_id = 1025
    language_id = 1866
    start_urls = ['https://debka.com/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        a = soup.select('#tag_cloud-5 > div > a')
        for i in a:
            response.meta['category1'] = i.text
            news_page_url =i.get('href')
            yield Request(url=news_page_url, callback=self.parse_page, meta=response.meta)
    def parse_page(self,response):
        time.sleep(3)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select('#content > div > article ')
        for i in a:
            t = i.select_one(' div.article-content.clearfix > div.below-entry-meta > span.posted-on > a > time').get('datetime')
            pub_time = t[0:10] + ' ' + t[11:-6]
        if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(pub_time):
             for i in a:
                news_url = i.select_one('div.article-content.clearfix > header > h2 > a').get('href')
                response.meta['title'] = i.select_one(' div.article-content.clearfix > header > h2 > a').text
                t = i.select_one('div.article-content.clearfix > div.below-entry-meta > span.posted-on > a > time').get('datetime')
                response.meta['time'] = t[0:10] + ' ' + t[11:-6]
                response.meta['abstract'] = i.select_one('div > p').text
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page_url = soup.select_one('#content > ul > li.previous > a').get('href')
                yield Request(url=next_page_url, callback=self.parse_page,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        try:
            a = soup.select('#post-132777 > div.article-content.clearfix > div.below-entry-meta > span.tag-links > a')
            if(len(a) > 1):
                item['category2'] = a[1].text
            else:
                item['category2'] = None
        except:
            item['category2'] = None
        try:
            pic = soup.select_one('#post-132777 > div.article-content.clearfix > div.featured-image > a > img').get('src')
            item['images'] = pic
        except:
            item['images'] = None
        item['body'] = soup.select_one('#post-132777 > div.article-content.clearfix > div.entry-content.clearfix > div.pf-content > p')
        yield item