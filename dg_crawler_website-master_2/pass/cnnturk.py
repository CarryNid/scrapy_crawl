# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from scrapy.http.request import Request


# author: 张珍珍
class CnnturkSpider(BaseSpider):
    name = 'cnnturk'
    allowed_domains = ['cnnturk.com']
    start_urls = ['http://cnnturk.com/']

    website_id = 1965
    language_id = 2227

    def parse(self, response):
        li_list = response.xpath('//ul[@class="sub-nav-list"]/li')
        li_list.pop(1)
        li_list.pop(2)
        for i in li_list:
            url = i.xpath('./a/@href').get()
            category1 = i.xpath('./a/span/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        link_list = response.xpath('//div[@class="swiper-wrapper"]/div | //div[@class="col-lg-6"] |'
                                 '//div[@class="col-12 col-md-3 col-lg-4"] | //div[@class="col-12 col-md-6 col-lg-4 special-col"] |'
                                 '//div[@class="row slide-sm-down"]/div')
        for i in link_list:
            url = 'http://cnnturk.com' + i.xpath('./a/@href').get()
            response.meta['title'] = i.xpath('./a/@aria-label').get()
            yield Request(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['abstract'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//h2[@class="detail-header-spot"]')])
        t = response.xpath('//p[@class="detail-header-info"]/text()').get().replace('.', ' ').split()
        item['pub_time'] = t[2] + '-' + t[1] + '-' + t[0] + ' ' + t[4]
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//section[@class="detail-content"]/p | //p[@class="card-spot"]')])
        item['images'] = ['https:' + i.xpath('./@src').get() for i in response.xpath('//figure[@class="detail-text-figure"]//img | //picture[@class="lazyloaded-parent"]/img')]
        yield item
