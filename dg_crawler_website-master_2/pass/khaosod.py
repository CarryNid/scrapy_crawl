# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from copy import deepcopy
import json


#   Author:叶雨婷
Tai_MONTH = {
        'ม.ค.': '01',
        'ก.พ.': '02',
        'มี.ค': '03',
        'เม.ย.': '04',
        'พ.ค.': '05',
        'มิ.ย.': '06',
        'ก.ค.': '07',
        'ส.ค.': '08',
        'ก.ย': '09',
        'ต.ล.': '10',
        'พ.ย.': '11',
        'ธ.ค.': '12'}

class KhaosodSpider(BaseSpider):
    name = 'khaosod'
    # allowed_domains = ['khaosod.co.th']
    start_urls = ['https://www.khaosod.co.th/']
    website_id = 1653
    language_id = 2208

    def parse(self, response):
        list_pages = response.xpath('//ul[@class="ud-mm__nav-menus"]/li/a/@href').getall()[1:6]
        for item in list_pages:
            meta_part = {'e': item}
            yield Request(url=item, callback=self.get_page, meta=meta_part)

    def get_page(self, response):
        t = response.xpath('//div[@class="row"]/div[@class="col-md-4"]//span[@class="udblock__updated_at"]/text()').getall()[-1].split(' ')
        if "ชั่วโมงก่อน" in t: # 有的时间是多少小时前
            last_time = DateUtil.time_now_formate()
        else:
            last_time = str(int(t[2]) - 543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
        meta = {'pub_time_': last_time}
        for item in response.xpath('//div[@class="row"]/div[@class="col-md-4"]//a/@href').getall():
            yield Request(url=item, callback=self.parse_pages, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            yield Request(url=response.xpath('//div[@class="udpg"]//li/a/@href').getall()[-1], callback=self.get_page, meta=deepcopy(meta))
            print(response.xpath('//div[@class="udpg"]//li/a/@href').getall()[-1])

    def parse_pages(self, response):
        item = NewsItem()
        print(111111111)
        item['title'] = ''.join((response.xpath('//h1[@class="udsg__main-title"]/text()').getall()[0].replace(' ',''))).strip()
        tt = response.xpath('//div[@class="udsg__meta-left"]/span/text()').getall()[0].split(' ')
        time = str(int(tt[2]) - 543) + "-" + Tai_MONTH[tt[1]] + "-" + str(tt[0]) + " 00:00:00"
        item['pub_time'] = time
        item['images'] = response.xpath('//div[@class="udsg__featured-image-wrap"]/a/@href').getall()
        item['body'] = ''.join(response.xpath('//div[contains(@itemprop,"articleBody")]/p/text()').getall())
        item['category1'] = response.xpath('//div[@class="udpgt"]//a/text()').getall()[0]
        item['abstract'] = ''.join(response.xpath('//div[contains(@itemprop,"articleBody")]//span/text()').getall())
        item['category2'] = response.xpath('//div[@class="udpgt"]//a/text()').getall()[1]
        print(response.xpath('//div[@class="udsg__featured-image-wrap"]/a/@href').getall())
        print(111111111)
        yield item




