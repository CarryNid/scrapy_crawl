# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

# author: 田宇甲
class DehujiangSpider(BaseSpider):  # 一个简单的静态爬虫，到底了就会报错然后停下来，分了article和news两种新闻都可以爬。
    name = 'dehujiang'
    website_id = 1798
    language_id = 1814
    start_urls = ['https://de.hujiang.com/new/xiaoyuan/']

    def parse(self, response):  # 留学咨讯新闻，怪怪的，也不多，但是能写就写了
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .m-lists .list-item'):
            time_ = i.select_one(' .info .tag').text + ':00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meat = {'title_': i.select_one(' .list-item-title').text.strip('\n'), 'time_': time_, 'category1_': '留学资讯', 'abstract_': i.select_one(' .list-item-desc').text}
                yield Request('https://de.hujiang.com'+i.select_one(' a:nth-child(2)')['href'], callback=self.parse_item, meta=meat)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'page' not in response.url:
                yield Request(response.url + '/page2/')
            else:
                yield Request(self.start_urls[0]+'/page'+str(int(response.url.split('/page')[1].strip('/'))+1)+'/')

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .article-content p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item


