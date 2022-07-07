# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from scrapy.http.request import Request


# author: 张珍珍
class MynetSpider(BaseSpider):
    name = 'mynet'
    # allowed_domains = ['mynet.com']
    start_urls = ['https://www.mynet.com/']

    website_id = 1823
    language_id = 2227


    def parse(self, response):
        li_list = response.xpath('//div[@class="my-open-menu"]/ul/li')[1:10]
        del li_list[2:4]
        del li_list[3:5]
        for i in li_list:
            category1 = i.xpath('./a/text()').get()
            new_url = i.xpath('./a/@href').get()
            yield Request(new_url, callback=self.parse_mulu, meta={'category1': category1})

    def parse_mulu(self, response):
        category1 = response.meta['category1']
        for j in response.xpath('//div[@class="iscroll-box-inner"]/ul/li'):
            category2 = j.xpath('./a/text()').get()
            url = j.xpath('./a/@href').get()
            if category2 == "Son Dakika" or category2 == "Rüya Tabirleri":
                continue
            yield Request(url, callback=self.parse_page, meta={'category1': category1, 'category2': category2})

    def parse_page(self, response):
        for i in response.xpath('//div[@class="sliderPost col-lg-8"]/div[2]//div')[1:]:
            url = i.xpath('./a/@href').get()
            response.meta['title'] = i.xpath('./a/@alt').get()
            yield Request(url, callback=self.parse_item, meta=response.meta)

        for i in response.xpath('//div[@class="card-body"]'):
            url = i.xpath('./h3/a/@href').get()
            response.meta['title'] = i.xpath('./h3/a/text()').get()
            yield Request(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] = response.xpath('//span[@class="post-date-mobile"]/time/@datetime').get()[:-6].replace('T',' ')
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['abstract'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//h2[@class="post-spot mb-0 pt-2 pb-2"]')])
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class="detail-content-inner"]/p | //div[@class="detail-content-inner mb-4"]/p')])
        item['images'] = [i.xpath('./@data-original').get() for i in response.xpath('//div[@class="detail-content-inner"]/p/img')]
        yield item
