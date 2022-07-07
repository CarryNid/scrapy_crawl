# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import requests


# author: 张珍珍
class MilliyetSpider(BaseSpider):
    name = 'milliyet'
    allowed_domains = ['milliyet.com.tr']
    start_urls = ['https://www.milliyet.com.tr/dunya/',
                  'https://www.milliyet.com.tr/ekonomi/',
                  'https://www.milliyet.com.tr/gundem/']

    website_id = 1960
    language_id = 2227

    def parse(self, response):
        li_list = response.xpath('//ul[@class="main-menu__nav-list"]/li')[1:-1]
        for i in li_list:
            url = 'http://milliyet.com.tr' + i.xpath('./a/@href').get()
            category1 = i.xpath('./a/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        l0 = response.css('a.cat-slider__link::attr(href)').extract()
        l1 = response.css('a.category-card.horizontal-news-card::attr(href)').extract()
        l2 = response.css('a.category-card.category-card--type-1::attr(href)').extract()
        l3 = response.css('a.category-card.category-card--type-2::attr(href)').extract()
        l4 = response.css('a.cat-list-card__link::attr(href)').extract()
        link_list = l0 + l1 + l2 + l3 + l4
        if link_list:
            flag = True
            if self.time is None:
                for i in link_list:
                    yield Request(url='http://milliyet.com.tr' + i, callback=self.parse_item, meta=response.meta)
            else:
                for i in link_list:
                    r = requests.get(url='http://milliyet.com.tr' + i)
                    last_time = r.xpath('//span[@class="hidden-md-up"]/time/@datetime').get()[:-6].replace('T', ' ')
                    if self.time < DateUtil.formate_time2time_stamp(last_time):  # 传入的时间比新闻发布的时间要早(时间戳要小)，也就是新闻很新
                        yield Request(url='http://milliyet.com.tr' + i, callback=self.parse_item, meta=response.meta)
                    else:
                        flag = False
                        self.logger.info("时间截止!")
            if flag:
                for i in self.start_urls:
                    for j in range(2, 6):
                        next_page = i + '?page={}'.format(str(j))
                        yield Request(url=next_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.xpath('//h1[@class="nd-article__title"]/text()').get()
        item['abstract'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//h2[@class="nd-article__spot"]')])
        try:
            item['pub_time'] = response.xpath('//span[@class="hidden-md-up"]/time/@datetime').get()[:-6].replace('T',' ')
        except:
            item['pub_time'] = ''
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class=" nd-content-column"]/p | //div[@class="text-container "]')])
        item['images'] = [i.xpath('./@data-src').get() for i in response.xpath('//div[@class="nd-article__spot-img"]/img | //div[@class="_picture"]/img | //div[@class="rhd-relative-container"]/a/img')]
        yield item
