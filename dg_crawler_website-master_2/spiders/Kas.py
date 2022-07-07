# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author: 王晋麟
class KasSpider(BaseSpider):
    name = 'Kas'
    website_id = 789
    language_id = 1901
    start_urls = ['https://www.kas.de/en/home']
    year = {
        'January': '1',
        'February': '2',
        'March': '3',
        'April': '4',
        'May': '5',
        'June': '6',
        'July': '7',
        'August': '8',
        'September': '9',
        'October': '10',
        'November': '11',
        'December': '12'
    }
    def parse(self, response):
        href_publication = response.xpath('//*[@id="navigation"]/div[2]/ul/li[4]/a/@href').extract()[0]
        yield Request(url=href_publication, callback=self.parse_news)

    def parse_news(self, response):
        news_hrefs = response.xpath('//*[@id="portlet_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_PUBLIKATIONEN"]/div/div/div/div[2]/div/a/@href').extract()
        for news_href in news_hrefs:
            news_url = 'https://www.kas.de' + news_href
            yield Request(url=news_url, callback=self.parse_item)
        nextpage_url = response.xpath('//*[@id="_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_PUBLIKATIONEN_ocerSearchContainerPageIterator"]/div/ul/li[3]/a/@href').extract()[0]
        if nextpage_url != 'javascript:;':  # 翻页
            yield Request(url=nextpage_url, callback=self.parse_news)

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.xpath('//*[@id="portlet_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_INTRO"]/div/div/div/div[2]/div[2]/h1/text()').extract()[0].replace('\n', '').strip()
        item['category1'] = 'news'
        item['category2'] = 'publications'
        contents = response.xpath('//*[@id="portlet_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_CONTENT"]/div/div/div/div[2]/div//text()').extract()
        body = ''
        for content in contents:
            body += content
        item['body'] = body.replace('\n', '').replace('\xa0', ' ').strip()
        item['abstract'] = response.xpath('//div[@class="c-page-intro__copy"]/text()').extract()[0].replace('\n', '').replace('\xa0', ' ').strip()
        times = response.xpath('//div[@class="c-page-intro__meta c-page-intro__meta--bottom"]/span/text()').extract()[1].replace('\n', '').strip().split(' ')
        pub_time = ''
        pub_time += times[2] + '-' + self.year[times[0]] + '-' + times[1].replace(',', '') + ' ' + '00:00:00'
        item['pub_time'] = pub_time
        item['images'] = []
        yield item
