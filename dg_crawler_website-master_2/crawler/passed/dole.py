# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.items import *
from crawler.spiders import BaseSpider
from scrapy.http.request import Request
from utils.date_util import DateUtil
from copy import deepcopy
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
    start_urls = ['https://www.dole.gov.ph']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        catagories = soup.select_one(" .pagelink a").get('href')
        yield Request(url=catagories, callback=self.parse2)

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select(" .post-content-text a")
        ssd = soup.select(" .grid-date-post")[-1].text.strip().split()
        if int(ssd[1].split(',')[0]) < 10:
            last = '0' + str(ssd[1].split(',')[0])
        else:
            last = ssd[1].split(',')[0]
        time_ = ssd[-1] + '-' + ENGLISH_MONTH[ssd[0]] + '-' + str(last) + ' 00:00:00'
        meta={'pub_time_':time_}
        # for article in articles:
        #     yield Request(url=article.get('href'), callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= self.time:
            for article in articles:
                yield Request(url=article.get('href'), callback=self.parse_item, meta=meta)
            yield Request(url=soup.select_one('.next.page-numbers').get('href'), callback=self.parse2,
                          meta=deepcopy(response.meta))
        else:
            self.logger.info("Time Stop")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select_one("h1.entry-title").text
        item['category1'] = 'news'
        item['category2'] = None
        item['body'] = "\n".join([i.text for i in soup.select(".entry-content p")[3:]])
        item['abstract'] = item['body'].split('\n')[0]
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = None
        yield item
        # 项目有时会超时报错，就是403，不用管它，数据是正常的
