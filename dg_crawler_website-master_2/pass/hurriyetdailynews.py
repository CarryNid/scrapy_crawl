from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date
import time


# author : 梁智霖
class HurriyetdailynewsSpider(BaseSpider):
    name = 'hurriyetdailynews'
    website_id = 1829
    language_id = 1866
    allowed_domains = ['hurriyetdailynews.com']
    start_urls = ['https://hurriyetdailynews.com']
    # is_http = 1 若网站使用的是http协议，需要加上这个类成员(类变量)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.col-md-9.col-sm-10 > ul > li > a')[0:2] + soup.select(
            'div.col-md-9.col-sm-10 > ul > li > a')[3:6]
        for category1 in categories:
            category_url = 'https://hurriyetdailynews.com' + category1.get('href')
            yield Request(url=category_url, callback=self.parse_page, meta={'category1': category1.text})


    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_time = time.strftime("%Y-%m-%d %H:%M:%S")
        articles = soup.select('div.module.news-single-complete ') + soup.select('div >div.news') + soup.select('ol >li')
        for article in articles:
            article_url = 'https://hurriyetdailynews.com' + article.select_one('a').get('href')
            title = article.select_one('a > h3').text
            yield Request(url=article_url, callback=self.parse_item,
                          meta={'category1': response.meta['category1'], 'title': title})

        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url=article_url, callback=self.parse_page)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=article_url, callback=self.parse_page)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        body = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.content > p')
             if paragraph.text != '' and paragraph.text != ' '])
        item['body'] = body
        abstract = soup.select_one('div.content > p').text
        item['abstract'] = abstract
        images = 'https:' + [img.get('src') for img in soup.select('div.content > img')][0]
        item['images'] = images
        time = soup.select_one('ul.info > li').text.split()
        pub_time = "{}-{}-{}".format(time[2], date.ENGLISH_MONTH[time[0]], time[1]) + ' ' + time[3]
        item['pub_time'] = pub_time
        yield item