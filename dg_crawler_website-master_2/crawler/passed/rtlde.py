# encoding: utf-8
from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import requests
from requests.adapters import HTTPAdapter
import re

de_month = {
        'Januar': '1',
        'Februar': '2',
        'März': '3',
        'April': '4',
        'Mai': '5',
        'Juni': '6',
        'Juli': '7',
        'August': '8',
        'September': '9',
        'Oktober': '10',
        'November': '11',
        'Dezember': '12'
    }

# author：欧炎镁
class RtldeSpider(BaseSpider):
    name = 'rtlde'
    # allowed_domains = ['rtl.de']
    start_urls = ['https://www.rtl.de/thema/0-9.html']
    website_id = 1765
    language_id = 1846
    custom_settings = {'DOWNLOAD_TIMEOUT': 60}
    proxy = '02'  # 需要
    api = 'https://www.rtl.de/thema/{0}-{1}.html'  # 用于获取不同主题
    ascii_n = int(96)  # 主题ascii码，获取以a-z开头的主题

    def parse(self, response):
        a_obj_list = response.css('a.rtlde-theme-item.event')
        for a_obj in a_obj_list:
            meta = {'category1':a_obj.css('div.text span').xpath('string(.)').extract_first()}
            page_link = a_obj.css('::attr(href)').extract_first()
            yield scrapy.Request(url='https://www.rtl.de/'+page_link, callback=self.parse_page,meta=deepcopy(meta))
        if self.ascii_n < 122:  # 获取以a-z开头的主题
            self.ascii_n += 1
            yield scrapy.Request(url=self.api.format(chr(self.ascii_n),chr(self.ascii_n)), callback=self.parse)

    def parse_page(self, response):
        item_link_list = response.css('a.teaser-link::attr(href)').extract()
        if item_link_list:
            flag = True
            if self.time is None:
                for item_link in item_link_list:
                    yield scrapy.Request(url=item_link, callback=self.parse_item,meta=deepcopy(response.meta))
            else:
                lengths = len(item_link_list) - 1  # 最后一个网址如果5次都拿不到也拿倒数第二个
                while True:
                    try:
                        s = requests.session()
                        s.mount('https://', HTTPAdapter(max_retries=1))  # 重试1次
                        response_item = s.get(url=item_link_list[lengths], timeout=60, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},proxies={'https': 'http://192.168.235.5:8888','http': 'http://192.168.235.5:8888'})
                        tt = scrapy.Selector(response_item).css('p.date-time::text').extract_first().replace('.',' ').replace('-','').split()
                        last_pub = DateUtil.formate_time2time_stamp("{}-{}-{} {}:00".format(tt[2],de_month[tt[1]],tt[0],tt[-1]))
                        break
                    except:
                        lengths -= 1
                if self.time < last_pub:
                    for item_link in item_link_list:
                        yield scrapy.Request(url=item_link, callback=self.parse_item, meta=deepcopy(response.meta))
                else:
                    self.logger.info("时间截止")
                    flag = False
            if flag:
                page_link = response.css('span.pagination__list__element.pagination__list__element--active + a::attr(href)').extract_first()  # 如果最后一页就会是None
                if page_link:
                    yield scrapy.Request('https://www.rtl.de/'+page_link, callback=self.parse_page,meta=deepcopy(response.meta))

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.css('h2.header__headline-title::text').extract_first()
        body = response.css('section[data-type="header"],section[data-type="text"],section[data-type="list"] ul li,section[data-type="gallery"] figure div.gallery-counter,section[data-type="gallery"] figure figcaption').xpath('string(.)').extract()
        item['body'] = '\n'.join([re.sub(r'(?<=[a-zäöüß])(?=[A-ZÄÖÜẞ])',' ',i,count=1).strip() for i in body]) # 列表里会出现标题粘着下一段开头的问题，找到第一个如‘zE’这样的搭配，然后再z和E之间加上一个空格
        tt = response.css('p.date-time::text').extract_first().replace('.',' ').replace('-','').split()
        item['pub_time'] = "{}-{}-{} {}:00".format(tt[2],de_month[tt[1]],tt[0],tt[-1])
        item['category1'] = ','.join(response.css('h2.font-lg::text').extract()) if response.css('h2.font-lg') else response.meta['category1']
        item['category2'] = None
        try:
            item['abstract'] = response.css('section.content[data-type="text"]')[0].xpath('string(.)').extract_first().split('.')[0] + '.' # 取第一句话作为abstract
        except:
            item['abstract'] = item['title']
        try:
            item['images'] = response.css('div.header-image img::attr(src),div.image-wrapper img::attr(src),section[data-type="gallery"] div.image-container img::attr(src),section[data-type="image"] img::attr(src)').extract()
        except:
            item['images'] = []
        yield item
