from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
import time

# author : 李玲宝
class TrtSpiderSpider(BaseSpider):
    name = 'trt'
    website_id = 1828
    language_id = 2227
    proxy = '02'
    start_urls = ['https://www.trt.net.tr/chinese/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('header>div.navigation a')
        for i in category1:
            yield scrapy.Request(url="https://www.trt.net.tr" + i['href'], callback=self.parse_page, meta={'category1': i.text})

    def parse_page(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('div.items>div>a')
        flag = True
        if self.time is not None:
            t = block[-1].select_one('time').text
            last_time = time.strftime('%Y-%m-%d', time.strptime(t, '%d.%m.%Y')) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for i in block:
                meta['time'] = time.strftime('%Y-%m-%d', time.strptime(i.select_one('time').text, '%d.%m.%Y'))
                yield Request(url="https://www.trt.net.tr" + i['href'], callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('li.next') == None:
                self.logger.info("no more pages")
            else:
                yield Request(url="https://www.trt.net.tr" + soup.select_one('li.next>a')['href'], callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.xpath('//div[@class="articleTitle"]/h1/text()').get()
        item['abstract'] = response.xpath('//div[@class="articleTitle"]/h2/text()').get()
        item['pub_time'] = meta['time']
        item['images'] = response.xpath('//figure//img/@src | //div[@class="slick-list draggable"]//img/@src').getall()
        item['body'] = '\n'.join([p.strip() for p in response.xpath('//div[@class="formatted"]//p//text()').getall()])
        return item
