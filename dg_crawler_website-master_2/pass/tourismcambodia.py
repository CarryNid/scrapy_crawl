# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
from utils.date_util import DateUtil
import re
#author:陈嘉玲
class TourismcambodiaSpider(BaseSpider):
    name = 'tourismcambodia'
    website_id = 1887
    language_id = 1866
    start_urls = ['https://www.tourismcambodia.com/']
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        li_list = soup.find_all(attrs={'class': 'nav navbar-nav'})
        flag = 0
        for category in li_list[0]:
            try:
                if flag >= 3:
                    break
                category_url = category.a['href']
                meta = {'category1': category.a.text}
                flag = flag + 1
            except:
                continue
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
    # part1 is ok
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles_1 = soup.find_all(attrs={'class': 'col-md-4 col-xs-12 g-mb-30'})  # 前两个
        articles_2 = soup.find_all(attrs={'class': 'col-md-4 col-sm-6 col-xs-12'})  # 第三个
        for i in articles_1:
            article_url = i.a['href']
            yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        for j in articles_2:
            article_url = j.a['href']
            yield Request(url=article_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            response.meta['title'] = soup.select_one('#category-title').text
        except:
            response.meta['title'] = soup.select_one('#main-2 > div > div.article-block > h1').text
        last_time = DateUtil.format_time_English('0')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['abstract'] = None
        item['pub_time'] = last_time
        item['category1'] = response.meta['category1']
        item['images'] = [img.get('src') for img in soup.select('img')]
        for i in soup.select('div > div > div.article > p'):
            try:
                item['body'] = i.text
            except:
                continue
        yield item


