from crawler.spiders import BaseSpider
from bs4 import BeautifulSoup
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from copy import deepcopy
from common.header import MOZILLA_HEADER
from lxml import etree
import requests


# author : 彭雨胜
class BengkuluekspressSpider(BaseSpider):
    name = 'bengkuluekspress'
    website_id = 34
    language_id = 1952
    start_urls = ['http://bengkuluekspress.com/']

    def parse(self, response):
        meta = response.meta
        categories1 = response.xpath('//*[@class="nav navbar-nav menu-inline zozo-main-menu"]/li')
        for category in categories1[0: -1]:
            meta['data'] = {'category1': category.xpath('.//a/text()').get(), 'category2': None}
            if category.xpath('.//a/@href').get() != '#':
                yield Request(url=category.xpath('.//a/@href').get(), callback=self.parse_page, meta=deepcopy(meta))
            for i in category.xpath('.//a')[1:]:
                page_link = i.xpath('./@href').get()
                category2 = i.xpath('./text()').get()
                meta['data']['category2'] = category2
                yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        meta = response.meta
        articles = response.xpath('//div[@class="newser-news"]/div[@class="row"]')
        if self.time is not None:
            if articles.getall():
                last_article_url = articles[-1].xpath('.//h4[@class="post-title"]/a/@href').get()
                tree = etree.HTML(requests.get(url=last_article_url, headers=MOZILLA_HEADER, timeout=5).text)
                last_time = tree.xpath('//*[@class="col-md-8 col-sm-7"]//li[@class="post-date"]/@content')[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                article_url = article.xpath('.//h4[@class="post-title"]/a/@href').get()
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//link[@rel="next"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath('//link[@rel="next"]/@href').get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem()
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = meta['data']['category2']
        item['title'] = response.xpath('//*[@class="col-md-8 col-sm-7"]//h1[@class="post-title"]/text()').get()
        item['pub_time'] = response.xpath('//*[@class="col-md-8 col-sm-7"]//li[@class="post-date"]/@content').get() + ' 00:00:00'
        item['body'] = '\n'.join([paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath('//div[@class="entry-summary"]/p | //div[@class="entry-summary"]/div')] if paragraph.strip() != '' and paragraph.strip() != '\xa0' and paragraph.strip() is not None])
        item['abstract'] = item['body'].split('\n')[0]
        soup = BeautifulSoup(response.text, 'lxml')
        item['images'] = [img.get('src') for img in soup.select('.post-content-wrapper img')]
        return item
