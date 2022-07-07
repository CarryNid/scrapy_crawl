# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

#author 马颢源
class modgovSpider(BaseSpider):
    name = 'mod.gov'
    website_id = 390
    language_id = 2036
    start_urls = ['https://www.mod.gov.my/ms/mediamenu/berita']

    def parse(self, response):
        flag = True
        if self.time is not None:

            time = response.xpath('//div[@class="span6"]//p[1].xpath(".//text()")').get().strip()
            time1 = time.substringbefore("-")
            time2 = time1.substringafter(",")
            last_time = time2[2] + '-' + time2[1] + '-' + time2[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            article_list = response.xpath('//div[@class="span6"]')
            for i in article_list:
                time = response.xpath('//div[@class="span6"]//p[1].xpath(".//text()")').get().strip()
                time1 = time.substringbefore("-")
                time2 = time1.substringafter(",")
                pub_time = time2[2] + '-' + time2[1] + '-' + time2[0] + ' 00:00:00'
                response.meta['abstract'] = i.xpath('//div[@class="span6"]//p.xpath(".//text()")').get().strip()
                response.meta['title'] = i.xpath('//div[@class="page-header"]//font//text()').get().strip()
                response.meta['images'] = i.xpath('//div[@class="span6"]//img').get()
                response.meta['pub_time'] = pub_time
                url = i.xpath('//div[@class="span6"]//h2/a/@href').get()
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = response.xpath('//li[@class="pagination-next"]/a/@href').get()
            if next_page:
                yield Request(url=next_page, callback=self.parse, meta=response.meta)  # 默认回调给parse()
            else:
                self.logger.info("no more pages")
    def parse2(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        yield item
