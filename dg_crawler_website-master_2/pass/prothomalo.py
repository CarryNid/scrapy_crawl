from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
import time

# author : 李玲宝
# check:why
class ProthomaloSpider(BaseSpider):
    name = 'prothomalo'
    website_id = 1921
    language_id = 1779
    start_urls = ['https://www.prothomalo.com/route-data.json?path=%2F']

    def parse(self, response):
        response = response.json()
        for i in response.get('config').get('sections'):
            url_part = i.get('section-url').split('https://www.prothomalo.com/')[-1]
            if '/' in url_part and i.get('section-url').startswith('https://www.prothomalo.com/') and url_part.split('/')[0] != 'video':
                url = 'https://www.prothomalo.com/route-data.json?path=/' + url_part
                yield scrapy.Request(url, callback=self.parse_page, meta={'category1': url_part.split('/')[0], 'category2': url_part.split('/')[1]})

    def parse_page(self, response):
        article = response.json().get('data').get('collection').get('items')
        if self.time is not None:
            t = article[-1].get('story').get('last-published-at') / 1000
            last_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for i in article:
                url = 'https://www.prothomalo.com/route-data.json?path=/' + i.get('story').get('url').split('https://www.prothomalo.com/')[-1]
                tt = i.get('story').get('last-published-at') / 1000  # 原时间戳是毫秒的，所以除10
                response.meta['pub_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tt))
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        article_body = response.json().get('data').get('story').get('cards')
        if response.json().get('pageType') == 'story-page' and article_body is not None:
            item = NewsItem()
            item['category1'] = response.meta['category1']
            item['category2'] = response.meta['category2']
            item['title'] = response.json().get('title')
            item['pub_time'] = response.meta['pub_time']
            item['images'] = []
            item['body'] = ''
            for i in article_body:  # 正文结构比较复杂
                for j in i.get('story-elements'):
                    if j.get('text') is not None:
                        if j.get('text').startswith('<'):
                            soup = BeautifulSoup(j.get('text'), 'html.parser')
                            item['body'] += soup.text.strip() + '\n'
                        else:
                            item['body'] += j.get('text').strip() + '\n'
                if i.get('metadata') is not None and i.get('metadata') != {}:
                    if i.get('metadata').get('social-share') is not None and i.get('metadata').get('social-share') != {}:
                        imageInfo = i.get('metadata').get('social-share').get('image')
                        if imageInfo is not None and imageInfo != {}:
                            item['images'].append('https://images.prothomalo.com/' + imageInfo.get('key'))
            item['body'] = item['body'].strip()
            item['abstract'] = item['body'].split('\n')[0]
            if item['body'] != '':
                return item
