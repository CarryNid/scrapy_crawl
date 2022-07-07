# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup


# author：凌俐
class chinaembassySpiderSpider(BaseSpider):
    name = 'chinaembassy'
    website_id = 1019
    language_id = 2266
    is_http = 1
    start_urls = ['http://www.chinaembassy.org.sg/chn/']
    sql = {
        'host': '121.36.242.178',
        'port': 3306,
        'user': 'dg_pub',
        'password': 'dg_pub',
        'db': 'dg_db_website'
    }

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = soup.select('#navigation > li > ul > li')
        for i in news_list:
            news_url = i.select_one('a').get('href')
            if not news_url.startswith("http"):
                news_urls = 'http://www.chinaembassy.org.sg/chn/' + news_url
                url = news_urls
                category1 = i.text
                yield Request(url=news_urls, meta={'url': url, 'category1': category1}, callback=self.parse_page)

    def parse_page(self, response):
        item = NewsItem()
        item['category1'] = response.meta['category1']
        soup = BeautifulSoup(response.text, 'html.parser')
        index = response.meta['url']
        eassy_list = soup.select('#docMore > li')
        for i in eassy_list:
            category2 = i.text
            url_list = i.select_one('a').get('href')
            if not url_list.startswith("http"):
                url_lists = index + url_list
                if not url_lists.endswith('pdf'):
                    yield Request(url=url_lists, meta={'category2': category2}, callback=self.eassy)
                else:
                    item['images'] = url_lists

    def eassy(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')

        if soup.select('#News_Body_Title'):
            item['title'] = soup.select_one('#article #News_Body_Title').string
            item['body'] = '\n'.join([i.text.strip() for i in soup.select('#News_Body_Txt_A > div > p')])
            item['pub_time'] = soup.select_one('#article #News_Body_Time').string
            item['category2'] = response.meta['category2']
            # print(item)
            yield item
        else:
            item['title'] = soup.select_one('#doctitle').string
            item['body'] = '\n'.join([i.text.strip() for i in soup.select('#content > div > p')])
            # print(item)
            item['pub_time'] = None
            item['category2'] = response.meta['category2']

            yield item


