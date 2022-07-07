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
# check: 凌敏 该网站已经写过
class zb_spider(BaseSpider):
    name = 'zb'
    website_id = 200
    language_id = 2266
    start_urls = ['https://www.zaobao.com/']

    def format_time(self,time):
        time = time.split(' ')
        time[0], time[2] = time[2], time[0]
        time[1] = str(common.date.ENGLISH_MONTH[time[1]])
        return ('-'.join(time)+" 00:00:00")

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        # print(soup.select('.nav-item > a'))
        for i in soup.select('.nav-item > a')[1:-2]:

            url = 'https://www.zaobao.com'+i.get('href')
            yield Request(url = url,callback=self.parse2)

    def parse2(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        more = soup.select('.title ~ a')

        if len(more) != 0 :
            for i in more:
                yield Request(url="https://www.zaobao.com"+i.get('href'),callback=self.parse2)

        else:
            id=None
            for i in soup.select('script'):
                if 'sitemap' in i.text:
                    id = eval(i.text.split('=')[-1])
            if id!=None:
                pageNo=2
                params = f"?pageNo={pageNo}&pageSize=18"
                meta = {"pageNo":pageNo,"id":id}
                api = "https://www.zaobao.com/more/sitemap/" + id + params
                # print(response.url)
                # print(api)
                yield Request(url=api,callback=self.essay_parser,meta = meta)

    def essay_parser(self,response):
        try:
            data = json.loads(response.text)
            _stamp = utils.date_util.DateUtil.formate_time2time_stamp(data['result']['data'][-1]['publicationDate'])
            for i in data['result']['data']:
                title = (i['title'])
                abstract = (i['contentPreview'])
                time = (i['publicationDate'])
                url = "https://www.zaobao.com"+(i['url'])
                meta={'title':title,
                      'abstract':abstract,
                      'time':time}
                yield Request(url = url,meta=meta,callback=self.essay_parser2)

            pageNo = response.meta['pageNo']+1
            id = response.meta['id']
            params = f"?pageNo={pageNo}&pageSize=18"
            meta = {"pageNo": pageNo, "id": id}
            api = "https://www.zaobao.com/more/sitemap/" + id + params
            if self.time == None or _stamp >= self.time:
                yield Request(url=api, callback=self.essay_parser, meta=meta)

        except:
            # print("WARNING:接口请求失败（已到最后一页/服务器无响应） ==> url:<",response.url,">")
            pass

    def essay_parser2(self,response):
        soup = BeautifulSoup(response.text, 'lxml')

        body = ''
        for i in soup.select('p'):
            body += i.text

        img=[]
        for i in soup.select('img'):
            img.append(i.get('src'))

        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = soup.select_one('ol > .active').text
        item['body'] = body
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['time']
        item['images'] = img
        yield item
