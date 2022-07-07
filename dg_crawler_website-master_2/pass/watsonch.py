# encoding: utf-8
from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import time
import requests
from requests.adapters import HTTPAdapter
from urllib import parse
import json

# author：欧炎镁
class WatsonchSpider(BaseSpider):
    name = 'watsonch'
    # allowed_domains = ['watson.ch']
    start_urls = ['https://www.watson.ch/u/tag_list']

    website_id = 1778
    language_id = 1846
    custom_settings = {'DOWNLOAD_TIMEOUT': 60}
    proxy = '02'  # 需要

    def parse(self, response):
        a_obj_list = response.css('div.widget.tags ul li a')
        for a_obj in a_obj_list[1:]: # 第一个标签是主页
            page_link = a_obj.css('::attr(href)').extract_first()
            meta = {'category1': a_obj.xpath('string(.)').extract_first(),'page_link':page_link}
            yield scrapy.Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        item_link_list = response.css('a.teaserlink::attr(href)').extract()
        if item_link_list:
            flag = True
            if self.time is None:
                for item_link in item_link_list:
                    if 'http' not in item_link:
                        item_link = 'https://www.watson.ch/' + item_link
                    yield scrapy.Request(url=item_link, callback=self.parse_item, meta=deepcopy(response.meta))
            else:
                lengths = len(item_link_list) - 1  # 最后一个网址如果5次都拿不到也拿倒数第二个
                last_pub = self.time - 1  # 如果拿不到时间就不要这页了
                while lengths:
                    try:
                        s = requests.session()
                        s.mount('https://', HTTPAdapter(max_retries=5))  # 重试5次
                        response_item = s.get(url=item_link_list[lengths], timeout=60, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},proxies={'https': 'http://192.168.235.5:8888','http': 'http://192.168.235.5:8888'})
                        last_pub = int(time.mktime(time.strptime(scrapy.Selector(response_item).css('div[class*="items-center text-xxs text-medium"]::text')[-1].extract(),"%d.%m.%Y, %H:%M")))
                        break
                    except:
                        lengths -= 1
                if self.time < last_pub:
                    for item_link in item_link_list:
                        if 'http' not in item_link:
                            item_link = 'https://www.watson.ch/' + item_link
                        yield scrapy.Request(url=item_link, callback=self.parse_item, meta=deepcopy(response.meta))
                else:
                    self.logger.info("时间截止")
                    flag = False
            if flag:
                next_page_link = response.css('div.widget.pagination ul li.current + li a::attr(href)').extract_first()
                if next_page_link:
                    yield scrapy.Request(response.meta['page_link']+next_page_link, callback=self.parse_page,meta=deepcopy(response.meta))

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.css('h2.watson-snippet__title').xpath('string(.)').extract_first()
        if item['title']:
            item['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(response.css('div[class*="items-center text-xxs text-medium"]::text')[-1].extract(),"%d.%m.%Y, %H:%M"))
            item['category1'] = ','.join(response.css('div.widget.tags ul li').xpath('string(.)').extract()) if response.css('div.widget.tags ul li') else response.meta['category1']
            item['category2'] = None
            # class下包含这些标签的文章内容是需要的，h3-h6这些是文章的子标题，li节点是列表下的节点只拿子节点没有a节点的li节点（因为有a的一般是推荐）
            body = response.xpath('//div[contains(@class,"watson-story__content")]//*[contains(@class,"watson-snippet__text") or contains(@class,"watson-snippet__quote__text")] | '
                                  '//div[contains(@class,"watson-story__content")]//*[self::h3 or self::h4 or self::h5 or self::h6] | '
                                  '//div[contains(@class,"watson-story__content")]//li[contains(@class,"watson-snippet__list__item")][not(a)]').xpath('string(.)').extract()
            item['body'] = '\n'.join([i.strip() for i in body])
            try:
                item['abstract'] = response.css('div.watson-snippet__lead').xpath('string(.)').extract_first() if response.css('div.watson-snippet__lead') else item['body'].split('.')[0] + '.'
            except:
                item['abstract'] = item['title']
            image1 = [i['payload'] for i in json.loads(parse.unquote(response.css('div.watson-story__content script[data-component="Slideshow"]').xpath('string(.)').extract_first()))['slideshowData']['images']] if response.css('div.watson-story__content script[data-component="Slideshow"]') else []
            image2 = ['https://www.watson.ch/'+i for i in response.css('div.watson-story__content img.watson-snippet__image.block.w-full.h-auto.bg-light ::attr(src), div.watson-story__content img.watson-gif__image::attr(src)').extract()] if response.css('div.watson-story__content img.watson-snippet__image.block.w-full.h-auto.bg-light, div.watson-story__content img.watson-gif__image') else []
            item['images'] = image1 + image2
            yield item
