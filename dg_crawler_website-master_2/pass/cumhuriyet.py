# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import requests
from lxml import etree
from common.header import MOZILLA_HEADER

month = {
    'Ocak': '01',
    'Şubat': '02',
    'Mart': '03',
    'Nisan': '04',
    'Mayıs': '05',
    'Haziran': '06',
    'Temmuz': '07',
    'Ağustos': '08',
    'Eylül': '09',
    'Ekim': '10',
    'Kasım': '11',
    'Aralık': '12'
}

# author: 张珍珍
class CumhuriyetSpider(BaseSpider):
    name = 'cumhuriyet'
    allowed_domains = ['cumhuriyet.com.tr']
    start_urls = ['http://cumhuriyet.com.tr/']
    myHeader = MOZILLA_HEADER
    website_id = 1969
    language_id = 2227
    myHeader['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'

    def parse(self, response):
        li_list = response.xpath('//ul[@class="main-links"]/li | //ul[@class="main-links black"]/li')[1:-1]
        li_list.pop(1)
        for i in li_list:
            url = 'https://cumhuriyet.com.tr' + i.xpath('./a/@href').get()
            category1 = i.xpath('./a/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1}, headers=self.myHeader)

    def parse_page(self, response):
        link_list = response.xpath('//div[@class="swiper-slide"] | //div[@class="haber-foto"]')
        if self.time is not None:
            if link_list:
                item = 'https://cumhuriyet.com.tr' + link_list[-1].xpath('./a/@href').get()
                tree = etree.HTML(requests.get(url=item, headers=self.myHeader).text)
                t = tree.xpath('//div[@class="yayin-tarihi"]/text()').get().split()
                last_time = t[2] + '-' + month[t[1]] + '-' + t[0] + ' ' + t[4]
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            for i in link_list:
                url = 'https://cumhuriyet.com.tr' + i.xpath('./a/@href').get()
                yield Request(url, callback=self.parse_item, meta=response.meta, headers=self.myHeader)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.xpath('//h1[@class="baslik"]/text()').get()
        t = response.xpath('//div[@class="yayin-tarihi"]/text()').get().split()
        item['pub_time'] = t[2] + '-' + month[t[1]] + '-' + t[0] + ' ' + t[4]
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = ''.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//h2[@class="spot"]')])
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class="col-sm-8 col-md-8 col-lg-8"]/div[6]/p |'
                                                                                            ' //div[@class="col-sm-8 col-md-8 col-lg-8"]/div[7]/p | //div[@class="haberMetni inread-ads"]//p')])
        item['images'] = ['https://cumhuriyet.com.tr' + i.xpath('./@src').get() for i in response.xpath('//img[@class="img-responsive mb20"] | '
                                                                                                         '//p[@lang="tr-TR"]/span/img')]
        yield item
