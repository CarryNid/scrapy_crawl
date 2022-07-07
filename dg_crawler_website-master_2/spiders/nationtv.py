# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
from copy import deepcopy
import json

#   Author:叶雨婷
Tai_MONTH = {
        'ม.ค.': '01',
        'ก.พ.': '02',
        'มี.ค.': '03',
        'เม.ย.': '04',
        'พ.ค.': '05',
        'มิ.ย.': '06',
        'ต.ค.': '07',
        'ก.ค.': '07',
        'ส.ค.': '08',
        'ก.ย.': '09',
        'ก.ย': '09',
        'ต.ล.': '10',
        'พ.ย.': '11',
        'ธ.ค.': '12'}

class NationtvSpider(BaseSpider):
    name = 'nationtv'
    index = 1
    start_urls = ['https://api.nationtv.tv/api/v1.0/categories/news/region?page={}'.format(index)]
    website_id = 1288
    language_id = 2181

    def parse(self, response):
        Dict = json.loads(response.text)
        Data = Dict['data']
        for datum in Data:
            href = datum['link']
            pub_time = datum['published_at'].split('T')[0] + " 00:00:00"
            meta = {'pub_time_': pub_time}
            yield Request(url="https://www.nationtv.tv" + datum['link'], callback=self.parse_pages, meta=meta)
            # print("https://www.nationtv.tv" + datum['link'])
            if self.time is None or DateUtil.formate_time2time_stamp(pub_time) >= int(self.time):
                try:
                    self.index = self.index + 1
                    yield Request(url='https://api.nationtv.tv/api/v1.0/categories/news/region?page={}'.format(self.index),
                                  callback=self.parse, meta=deepcopy(meta))
                except AttributeError:
                    pass

        # 用来打开网页json文件的代码
        # with open('nationtv.json','w') as f:
        #     Nation_json = json.dumps(response.json(), ensure_ascii=False)
        #     f.write(Nation_json)

    def parse_pages(self, response):
        item = NewsItem()
        # 进入后文章内是静态的了，只是动态加载广告一类
        item['title'] = ''.join(response.xpath('//h1[@class="category"]/text()').getall())
        t = response.xpath('//ul[@class="dateUpdate"]/li/text()').getall()[0].split(' ')
        item['pub_time'] = str(int(t[2]) - 543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
        item['images'] = response.xpath('//picture/img/@src').getall()
        item['body'] = ''.join(response.xpath('//div[@class="content-detail"]/p/text()').getall())
        item['abstract'] = response.xpath('//h2[@class="content-blurb"]/text()').getall()
        item['category1'] = response.xpath('//div[@class="title"]/text()').getall()[1].split(' ')[0]
        item['category2'] = response.xpath('//div[@class="title"]/strong/text()').getall()
        # print(response.xpath('//div[@class="content-detail"]/p/text()').getall())
        yield item

