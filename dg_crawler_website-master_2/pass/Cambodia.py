import re

import scrapy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# auuthor:蔡浩杰
class Cambodia(BaseSpider):
        name = 'Cambodia'
        website_id = 1885
        language_id = 1813
        start_urls = ['https://www.quyazhou.com/site/tourismcambodia.html']

        def parse(self, response):
            more_herf = response.xpath('//ul[@class="list"]/li/a[@class="preview"]/@href').extract()
            time_list = response.xpath('//p[@class="time"]/span[@class="sta"]/text()').extract()
            time_list_1=[]
            for time in time_list:
                time_list_1.append("{:s} 00:00:00".format(str(time)[3::]))
            response.meta['time_list_1']=time_list_1
            for herf in more_herf:
                more_herf = 'https://www.quyazhou.com/{:s}'.format(herf)
                yield scrapy.Request(url=more_herf, callback=self.page_parse, meta=response.meta)

        def page_parse(self, response):
            title_list = response.xpath('//main[@id="content"]/h1/text()')[0].extract()
            abstract_text=response.xpath('//p[1]/text()')[0].extract()
            response.meta['abstract']=abstract_text
            content_text = response.xpath('//p/text()').extract()
            content_text = ''.join(content_text)
            response.meta['content_text'] = content_text
            response.meta['title_list'] = title_list

            item = NewsItem()
            item['abstract']=response.meta['abstract']
            len_1 = len(response.meta['time_list_1'])
            for i in range(0, len_1):
                item['pub_time'] = response.meta['time_list_1'][i]
            item['title'] = response.meta['title_list']
            item['body'] = response.meta['content_text']
            yield item
