# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
# author: 何镓乐
ENGLISH_MONTH = {
        'জানুয়ারী': '01',
        'ফেব্রুয়ারী': '02',
        'মার্চ': '03',
        'এপ্রিল': '04',
        'মে': '05',
        'জুন': '06',
        'জুলাই': '07',
        'আগস্ট': '08',
        'সেপ্টেম্বর': '09',
        'অক্টোবর': '10',
        'নভেম্বর': '11',
        'ডিসেম্বর': '12'}
class WordpressSpider(BaseSpider):
    name = 'wordpress'
    website_id = 1906
    language_id = 1779
    start_urls = ['https://lalonsain.wordpress.com/page/1/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = soup.select('#content-body .post-date a').get('href')
        for ur in urls:
            ssd = soup.select('#content-body .post-date').text.strip().split(',').strip().split(' ')
            time_ = ssd[-1] + '-' + ENGLISH_MONTH[ssd[0]] + '-' + ssd[1] + ' 00:00:00'
            meta = {'pub_time_': time_}
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                yield Request(url=ur, callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
            yield Request(response.url.replace(response.url.split('page/')[1].split('/')[0], str(int(response.url.split('page/')[1].split('/')[0])+1)))

    def parse_item(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select_one(' #content-body h1').text
        item['category1'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.entry > p')])
        item['abstract'] = item['body']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = None
