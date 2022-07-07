'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-07 23:00:32
LastEditors: Renhetian
LastEditTime: 2022-02-07 23:08:07
'''
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class MbsSpider(BaseSpider):
    name = 'mbs'
    website_id = 2004
    language_id = 1963
    start_urls = ['http://www.mbs.jp/']

    News_url = 'http://www.mbs.jp/news/'
    def parse(self, response):
        page_url = response.xpath('//*[@id="news-new"]/div/div[1]/div/a/@href').extract_first()
        yield scrapy.Request(url=page_url, callback=self.parse_detail)

    def parse_detail(self, response):
        news_href_list = response.xpath('//*[@id="genre"]/div[2]/div[2]//li/a/@href').extract()
        for li in news_href_list:
            news_url = self.News_url + li.replace("../", "")
            yield scrapy.Request(url=news_url, callback=self.Item)

    def Item(self, response):
        item = NewsItem()
        content_list = response.xpath('//*[@id="article"]/p[2]//text()').extract()
        main_content = "".join(content_list).replace("\n", "").replace("\u3000", "").replace(" ", "")
        Abstr = list(main_content.split('。'))[0]
        item['title'] = response.xpath('//*[@id="article"]/h3/text()').extract_first()
        item['category1'] = '新闻资讯'
        item['category2'] = '关西新闻'
        item['body'] = main_content
        item['abstract'] = Abstr
        item['pub_time'] = response.xpath('//*[@id="article"]/p[1]/text()').extract_first().replace("更新：", "").replace("/", "-") + ":00"
        item['images'] = None
        yield item
