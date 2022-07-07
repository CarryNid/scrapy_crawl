# encoding: utf-8
from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import requests
from requests.adapters import HTTPAdapter
import re
import time
from bs4 import BeautifulSoup
import sys

# author：欧炎镁
class ClalitcoilSpider(BaseSpider):
    name = 'clalitcoil'
    allowed_domains = ['clalit.co.il']
    start_urls = ['https://www.clalit.co.il/he/_layouts/15/ClalitInfo/Pages/AjaxCallsData.aspx/GetPromotedArtices']
    website_id = 1938
    language_id = 1926
    custom_settings = {'DOWNLOAD_TIMEOUT': 100}
    sys.setrecursionlimit(10000000) # 防止Beautifulsoup解析时发生栈溢出
    proxy = '02'

    def start_requests(self):
        s = requests.session()
        s.mount('https://', HTTPAdapter(max_retries=5))  # 重试5次 改一下代理
        response = s.post(url=self.start_urls[0], timeout=60, headers={'X-Requested-With': 'XMLHttpRequest','Content-Type': 'application/json; charset=UTF-8',"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},proxies={'https': 'http://192.168.235.5:8888', 'http': 'http://192.168.235.5:8888'})
        for i in response.json()['d']:
            meta = {'category1': i['Title']}
            yield scrapy.Request('https://www.clalit.co.il' + i['worldHomeURL'], callback=self.parse,meta=deepcopy(meta))

    def parse(self, response):
        a_obj_list = response.css('div.carousel-item.active a.card,a.card-body')
        for a_obj in a_obj_list:
            if a_obj.css('p'):
                response.meta['category2'] = a_obj.css('p').css('::text').extract_first()
            page_link = a_obj.css('::attr(href)').extract_first()
            if page_link.split('/')[-1] == 'default.aspx':
                yield scrapy.Request('https://www.clalit.co.il'+page_link, callback=self.parse, meta=deepcopy(response.meta))
            else:
                yield scrapy.Request('https://www.clalit.co.il'+page_link, callback=self.parse_page, meta=deepcopy(response.meta))

    def parse_page(self, response):
        div_obj_list = response.css('div.articles-list-details')
        if div_obj_list:  # 如果新闻列表有新闻
            flag = True
            if self.time is None:
                for div_obj in div_obj_list:
                    response.meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('p.article-date::text').re('\d+/\d+/\d+')[0],"%d/%m/%Y")) if div_obj.css('p.article-date') else DateUtil.time_now_formate()
                    response.meta['title'] = div_obj.css('p.h3 a::text').extract_first()
                    response.meta['abstract'] = div_obj.css('p.article-description a::text').extract_first() if div_obj.css('p.article-description a::text') else None
                    item_link = 'https://www.clalit.co.il' + div_obj.css('p.h3 a::attr(href)').extract_first()
                    yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(response.meta))
            else:
                last_pub = int(time.mktime(time.strptime(div_obj_list[-1].css('p.article-date::text').re('\d+/\d+/\d+')[0],"%d/%m/%Y")))
                if self.time < last_pub:
                    for div_obj in div_obj_list:
                        response.meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('p.article-date::text').re('\d+/\d+/\d+')[0], "%d/%m/%Y")) if div_obj.css('p.article-date') else DateUtil.time_now_formate()
                        response.meta['title'] = div_obj.css('p.h3 a::text').extract_first()
                        response.meta['abstract'] = div_obj.css('p.article-description a::text').extract_first().strip() if div_obj.css('p.article-description a::text') else None
                        item_link = 'https://www.clalit.co.il' + div_obj.css('p.h3 a::attr(href)').extract_first()
                        yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(response.meta))
                else:
                    self.logger.info("时间截止")
                    flag = False
            if flag:
                try:
                    next_page_link = 'https://www.clalit.co.il' + response.css('li.page-item.active + li a::attr(href)').extract_first()
                    yield scrapy.Request(next_page_link, callback=self.parse_page, meta=deepcopy(response.meta))
                except:
                    pass

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = '\n'.join([j.strip() for j in [re.sub(r'<.*?>','',str(i).replace('<br/>','\n')) for i in BeautifulSoup(response.text, 'lxml').select('div.ms-rtestate-field >*:not(table)')] if j.strip() != ''])
        item['images'] = ['https://www.clalit.co.il' + img for img in response.css('div.article-image-lg img,div.ms-rtestate-field img').css('::attr(src)').extract()]
        item['abstract'] = item['body'].split('\n')[0] if ((not response.meta['abstract']) and item['body']) else response.meta['abstract']
        yield item