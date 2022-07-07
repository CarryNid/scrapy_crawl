# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.items import *
from crawler.spiders import BaseSpider
from scrapy.http.request import Request
from utils.date_util import DateUtil
import re

# author:robot_2233
ENGLISH_MONTH = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'}  # 这个字典感觉比common里面的好用，毕竟是要转成时间戳的


class doleSpiderSpider(BaseSpider):
    name = 'dole'
    website_id = 1259
    language_id = 1866
    start_urls = ['https://www.dole.gov.ph/good-news-archive/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all(class_=re.compile('news type-news news-col-list'))
        for article in articles:
            ssd = soup.select_one(" .grid-date-post").text.strip().split()
            if int(ssd[1].split(',')[0]) < 10:
                last = '0' + str(ssd[1].split(',')[0])
            else:
                last = ssd[1].split(',')[0]
            time_ = ssd[-1] + '-' + ENGLISH_MONTH[ssd[0]] + '-' + str(last) + ' 00:00:00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meta = {'pub_time_': time_}
                yield Request(url=article.a.get('href'), callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(url=soup.select_one(' .next.page-numbers').get('href'))

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select(" .entry-content p")[2].text
        item['category1'] = 'Good-news-archive'
        item['category2'] = None
        item['body'] = "\n".join([i.text for i in soup.select(" .entry-content p")[3:]])
        item['abstract'] = soup.select(" .entry-content p")[3]
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = None
        yield item
