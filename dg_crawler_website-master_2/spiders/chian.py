# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
from copy import deepcopy
from common.date import ENGLISH_MONTH

#   Author:叶雨婷

class ChianSpider(BaseSpider):
    name = 'chian'
    # allowed_domains = ['chiangraitimes.com']
    start_urls = ['https://www.chiangraitimes.com/th/news']
    website_id = 1585
    language_id = 2208

    def parse(self, response):
        t = response.xpath('//time[@class="entry-date updated td-module-date"]/text()').getall()[-1]
        last_time = t + " 00:00:00"
        meta = {'pub_time_': last_time}
        for i in response.xpath('//div[@id="tdi_90"]//div[@class="td-module-thumb"]/a'):
            yield Request(url=i.xpath('@href').getall()[0], callback=self.parse_pages, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            print(response.xpath('//div[@class="page-nav td-pb-padding-side"]/a[@aria-label="next-page"]/@href').getall())
            yield Request(url=response.xpath('//div[@class="page-nav td-pb-padding-side"]/a[@aria-label="next-page"]/@href').getall()[0],
                          callback=self.parse_pages, meta=deepcopy(meta))
        else:
            self.logger.info("Time Stop")

    # 填表的
    def parse_pages(self, response):
        item = NewsItem()
        title = response.xpath('//h1[@class="tdb-title-text"]/text()').getall()
        if title == ['News']:
            item['title'] = None
        else:
            item['title'] = title
        try:
            time = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/time[@class="entry-date updated td-module-date"]/text()').getall()[0]
            item['pub_time'] = time + " 00:00:00"
        except:
            item['pub_time'] = None
        item['images'] = response.xpath('//img/@src').getall()
        body = ''.join(response.xpath('//div[@class="tdb-block-inner td-fix-index"]/p/text()').getall())
        if body=='':
            item['body'] = None
        else:
            item['body'] = body
        item['category1'] = None
        item['abstract'] = None
        try:
            item['category2'] = response.xpath('//a[@class="tdb-entry-category"]/text()').getall()[0]
        except:
            item['category2'] = None
        yield item




