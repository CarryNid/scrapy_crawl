# encoding: utf-8
import html
import json

from bs4 import BeautifulSoup

import common
import utils.date_util
from common.date import ENGLISH_MONTH
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import time

# Author:陈卓玮
# check: 凌敏 pass
class govsg_spider(BaseSpider):
    name = 'govsg'
    website_id = 199
    language_id = 1866
    start_urls = ['https://www.gov.sg/']

    def format_time(self,time):
        time = time.split(' ')
        time[0], time[2] = time[2], time[0]
        time[1] = str(common.date.ENGLISH_MONTH[time[1]])
        return ('-'.join(time)+" 00:00:00")

    def parse(self, response):
        category=['Factually','Explainers','Stories','Interviews']

        for cate_name in category:
            params = f"fq=contenttype_s:{cate_name}&" \
                     "sort=publish_date_tdt desc&" \
                     "start=1&rows=50"

            api = 'https://www.gov.sg/api/v1/search'
            meta={'start':1,'rows':50,'cate_name':cate_name}
            time.sleep(5)
            yield Request(url = api+"?"+params,callback=self.parse_essay,meta=meta)

    def parse_essay(self,response):
        cate_name = response.meta['cate_name']
        start=response.meta['start']
        rows=response.meta['rows']
        item = NewsItem()
        data = json.loads(response.text)
        if len(data['response']['docs'])!=0:
            try:
                time_stamp=utils.date_util.DateUtil.formate_time2time_stamp(self.format_time(data['response']['docs'][-1]['publishdate_s']))
            except:
                time_stamp=utils.date_util.DateUtil.formate_time2time_stamp('2010-01-01 00:00:00')##当翻到最后一页时 文章没有时间

            for i in data['response']['docs']:
                try:
                    item['category2'] = i['primarytopic_s']
                except:
                    pass

                try:
                    item['abstract'] = i['short_description_t']
                except:
                    item['abstract'] = html.escape(i['bodytext_t'].split('\n')[0])
                item['images'] = []
                item['images'].append(i['imageurl_s'])
                item['body'] = i['bodytext_t']
                item['pub_time'] = self.format_time(i['publishdate_s'])
                item['title'] = html.escape(i['title_t'])
                item['category1'] = i['contenttype_s']
                try:
                    t_stamp = utils.date_util.DateUtil.formate_time2time_stamp(self.format_time(i['publishdate_s']))
                except:
                    t_stamp = utils.date_util.DateUtil.formate_time2time_stamp('2010-01-01 00:00:00')

                if self.time == None or t_stamp >= self.time:
                    yield item

            if self.time == None or time_stamp >= self.time :
                start = start+rows
                params = f"fq=contenttype_s:{cate_name}&" \
                         "sort=publish_date_tdt desc&" \
                         f"start={start}&rows={rows}"
                meta={'start':start,'rows':rows,'cate_name':cate_name}
                api = 'https://www.gov.sg/api/v1/search'
                time.sleep(5)
                yield Request(url = api+"?"+params,callback=self.parse_essay,meta=meta)

