# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.items import *
from crawler.spiders import BaseSpider
from scrapy.http.request import Request
from utils.date_util import DateUtil
from copy import deepcopy

#author:robot-2233
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
        'December': '12'}

class daSpiderSpider(BaseSpider):
    name = 'da'
    website_id = 1261
    language_id = 1866
    start_urls = ['https://www.da.gov.ph/news/']

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select(' .post-details')[-1].text.strip().split('|')[-1].split()
        if int(ssd[0])<10:
            ssd[0]='0'+str(ssd[0])
        time_ = ssd[-1] + '-' + ENGLISH_MONTH[ssd[1]] + '-' + str(ssd[0]) + ' 00:00:00'
        meta = {'pub_time_': time_}
        # for i in soup.select(' .post-wrap a')[::3]:
        #     yield Request(url=i.get('href'),callback=self.parse_item,meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= self.time:
            for i in soup.select(' .post-wrap a')[::3]:
                yield Request(url=i.get('href'), callback=self.parse_item, meta=meta)
            if soup.select_one('.paging .current+a') is not None:
                yield Request(url=soup.select_one('.paging .current+a').get('href'), callback=self.parse,meta=deepcopy(meta))
        else:
            self.logger.info("Time Stop")


    def parse_item(self, response):
        soup=BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select_one(' .col-sm-8 h1').text
        item['category1'] = soup.select_one(' #crumbs').text
        item['category2'] = None
        item['body'] = soup.select_one('article').text.strip()
        item['abstract'] = item['body'].split('\n')[0]
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = soup.select_one(' article img').get('src')
        yield item
