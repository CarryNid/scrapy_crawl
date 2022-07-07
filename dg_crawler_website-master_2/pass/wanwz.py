# encoding: utf-8
import os
import requests
import scrapy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

#author: 张景深
class QvyazhouSpider(BaseSpider):
    name = 'qvyazhou43'
    website_id = 1217
    language_id = 1895
    start_urls = ['https://www.quyazhou.com/site/tourismcambodia.html']
    def parse(self, response):
        item = NewsItem()
        more_herf = response.xpath('//ul[@class="list"]/li/a[@class="preview"]/@href').extract()
        div_list = response.xpath('//div[@id="info-content"]/ul/li')
        images_list=[]
        times_list=[]
        for div in div_list:
            time = div.xpath('.//p/span/text()')[0].extract()
            src = div.xpath('.//img/@src')[0].extract()
            image="http://www.qvyazhou.com"+src
            images_list.append(image)
            new_time = time.strip('开始：') + " " + "00:00:00"
            times_list.append(new_time)
        response.meta['images_list'] = images_list
        response.meta['times_list'] = times_list
        for herf in more_herf:
            more_herf = 'https://www.quyazhou.com/{:s}'.format(herf)
            yield scrapy.Request(url=more_herf, callback=self.page_parse, meta=response.meta)

    def page_parse(self, response):
        title_list = response.xpath('//main[@id="content"]/h1/text()')[0].extract()
        abstract_text = response.xpath('//p[1]/text()')[0].extract()
        response.meta['abstract'] = abstract_text
        content_text = response.xpath('//p/text()').extract()
        content_text = ''.join(content_text)
        response.meta['content_text'] = content_text
        response.meta['title_list'] = title_list

        item = NewsItem()
        item['abstract'] = response.meta['abstract']
        len_1 = len(response.meta['images_list'])
        for i in range(0, len_1):
            item['images'] = response.meta['images_list'][i]
        len_2 = len(response.meta['images_list'])
        for i in range(0, len_2):
            item['pub_time'] = response.meta['times_list'][i]
        item['title'] = response.meta['title_list']
        item['body'] = response.meta['content_text']
        yield item
