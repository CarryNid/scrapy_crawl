# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


# author:马颢源
class mohrgovSpider(BaseSpider):
    name = 'mohrgov'
    start_urls = ['https://www.mohr.gov.my/index.php/ms/latest-articles-2']
    website_id = 396
    language_id = 2036

    def parse(self, response):
        flag = True
        if self.time is not None:
            time = response.xpath('//div[@class="itemList"]//h3[@class="itemTitle"]/a/text()').get().strip()
            time1 = time.split('(')[1].split(')')[0]
            time2 = time1.split('.')
            last_time = time2[2] + '-' + time2[1] + '-' + time2[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            article_list = response.xpath('//div[@class="itemList"]//h3[@class="itemTitle"]')
            for i in article_list:
                url = i.xpath('//div[@class="itemList"]//h3[@class="itemTitle"]/a/@href').get()
                time = response.xpath('//div[@class="itemList"]//h3[@class="itemTitle"]/a/text()').get().strip()
                time1 = time.split('(')[1].split(')')[0]
                time2 = time1.split('.')
                pub_time = time1[2] + '-' + time1[1] + '-' + time1[0] + ' 00:00:00'
                response.meta['title'] = i.xpath('//div[@class="itemList"]//h3[@class="itemTitle"]/a/text()').get()
                response.meta['abstract']=i.xpath('//div[@class="itemList"]//h3[@class="itemTitle"]/a/text()').get()
                response.meta['pub_time'] = pub_time
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

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = None
        item['category2'] = None
        item['abstract'] = response.meta['abstract']
        yield item