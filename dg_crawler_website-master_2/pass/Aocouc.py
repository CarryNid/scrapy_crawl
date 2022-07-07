# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


# author: 王晋麟
class AocoucSpider(BaseSpider):
    name = 'Aocouc'
    website_id = 820
    language_id = 1813
    start_urls = ['http://aoc.ouc.edu.cn/main.htm']

    def parse(self, response):
        category1_href = response.xpath('//*[@id="nav"]/div/div/div/ul/li/a/@href').extract()[4]
        category1_url = "http://aoc.ouc.edu.cn" + category1_href
        yield Request(url=category1_url, callback=self.parse_detail)

    def parse_detail(self, response):
        category2_hrefs = response.xpath('//*[@id="l-container"]/div/div/div[1]/div[2]/div/ul/li/a/@href').extract()
        for category2_href in category2_hrefs:
            category2_url = "http://aoc.ouc.edu.cn" + category2_href
            yield Request(url=category2_url, callback=self.parse_news)

    def parse_news(self, response):
        news_hrefs = response.xpath('//*[@id="wp_news_w6"]/ul/li//a/@href').extract()
        for news_href in news_hrefs:
            news_url = "http://aoc.ouc.edu.cn" + news_href
            yield Request(url=news_url, callback=self.parse_item)
        nextpage_href = response.xpath('//*[@class="next"]/@href').extract()[0]
        if nextpage_href != 'javascript:void(0);':  # 翻页
            nextpage_url = "http://aoc.ouc.edu.cn" + nextpage_href
            yield Request(url=nextpage_url, callback=self.parse_news)

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.xpath('//*[@id="d-container"]/div/div/div/h1/text()').extract()[0]
        item['category1'] = 'news'
        item['category2'] = '海洋要闻'
        contents = response.xpath('//*[@id="d-container"]/div/div/div/div/div/div/p//text()').extract()
        body = ''
        for content in contents:
            body += content
        item['body'] = body
        item['abstract'] = list(body.split('。'))[0]
        item['pub_time'] = response.xpath('//*[@class="arti_update"]/text()').extract()[0].replace('发布时间：',"") + " 00:00:00"
        item['images'] = []
        try:
            srcs = response.xpath('//*[@id="d-container"]/div/div/div/div/div/div//img/@src').extract()
            for src in srcs:
                image = "http://aoc.ouc.edu.cn" + src
                item['images'].append(image)
        except:
            item['images'] = None
        yield item
