
# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
#author: robot_2233

class nhandanSpiderSpider(BaseSpider):
    name = 'nhandanvn'
    website_id = 2048
    language_id = 2242 # 越南语
    #本爬虫实验性直接请求了网站源码,有意思
    start_urls = [f'https://nhandan.vn/article/Paging?categoryId={i}&pageIndex=1&pageSize=50&fromDate=&toDate=&displayView=PagingPartial' for i in ['1251','1171','1185','1211','1287','1257','1231','1224','1303','1309','1292','1296','1315']]


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' article'):
            ssd = i.select_one(' .box-meta-small').text.split(' ')
            time_ = ssd[1].split('/')[-1] + '-' + ssd[1].split('/')[1] + '-' + ssd[1].split('/')[0] + ' ' + ssd[0] + ':00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meta = {'pub_time_': time_}
                yield Request(url='https://nhandan.vn'+i.select_one(' .box-title').a.get('href'),  callback=self.parse_item,meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
            tyj=str(response.url).split('&pageSize=')[0].split('&pageIndex=')[0]+'&pageIndex='+str(int(str(response.url).split('&pageSize=')[0].split('&pageIndex=')[1])+1)+'&pageSize=50&fromDate=&toDate=&displayView=PagingPartial'
            yield Request(tyj) #自增


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] =soup.select_one(' .box-title-detail.entry-title').text
        item['category1'] = 'All'
        item['category2'] = None
        item['body'] =soup.select_one(' .detail-content-body').text
        item['abstract'] =soup.select_one(' .box-des-detail.this-one').text.strip('\n')
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] =[soup.select_one(' .box-detail-thumb.uk-text-center').img.get('src')]
        except:
            item['images'] = []
        return item # 爬虫虽小，五脏俱全