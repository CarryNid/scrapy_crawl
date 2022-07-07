import json
import random
import re


from bs4 import BeautifulSoup
from scrapy import Request
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil

class XinhuamyanmarMmcnSpider(BaseSpider):
    name = 'xinhuamyanmar_mmcn'
    allowed_domains = ['xinhuamyanmar.com']
    start_urls = ['https://xinhuamyanmar.com/mm-cn/']
    website_id = 1659
    language_id = 2065 # 中缅双语，1813（中）
    api = 'https://xinhuamyanmar.com/mm-cn/page/{}/'
    proxy = random.choice(['01','00','02'])

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        flag = True
        last_pub = soup.select('.mvp-blog-story-list > li > a')[-1]
        last = DateUtil.format_time_English(last_pub.select_one('.mvp-cd-date').text)
        if self.time is None or self.time <= DateUtil.formate_time2time_stamp(last):
            for i in soup.select('.mvp-blog-story-list > li > a'):
                meta = {
                    'category1':i.select_one('.mvp-cd-cat.left.relative').text,
                    'mtitle': i.select_one('h2').text,
                    'pub_time':DateUtil.format_time_English(i.select_one('.mvp-cd-date').text)
                }
                yield Request(url=i.get('href'), callback=self.parse_item, meta=meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            for i in range(2,80):   # 2022-01-13 该网站栏目只不到70页，所以循环这么多次
                yield Request(url=self.api.format(str(i)))

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['images'] =  [i.get('src') for i in soup.select('#mvp-post-main img')]
        item['title'] = response.meta['mtitle']
        item['pub_time'] = re.findall('\d+-\d+-\d+ \d+:\d+:\d+',response.text)[0] if re.findall('\d+-\d+-\d+ \d+:\d+:\d+',response.text) else response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = self.parseBu_Zh(soup.select('#mvp-content-main > p'))[0]  # mBody
        item['abstract'] = item['body'].split('\n')[0]
        yield item
        item['language_id'] = 1813
        item['body'] = self.parseBu_Zh(soup.select('#mvp-content-main > p'))[1]
        item['abstract'] = item['body'].split('\n')[0]
        yield item

    @staticmethod
    def parseBu_Zh(pList:list):
        allStr = '\n'.join([i.text.strip(' \n') for i in pList])
        sep = re.findall('\n…*\n',allStr)[0] if re.findall('\n…*\n',allStr) else None
        if not sep:
            sep = re.findall('——*', allStr)[0] if re.findall('——*"', allStr) else None
        version = re.findall('([a-zA-Z]+ Version)', allStr)[0]
        if not sep:
            sep = version
        mBody = allStr.split(sep)[0]
        tt = re.findall('\d+-\d+-\d+ \d+:\d+:\d+',allStr)[0]
        # version = re.findall('([a-zA-Z]+ Version)',allStr)[0]
        zBody = allStr.split(sep)[1].replace(tt,'').replace(version,'')
        return (mBody,zBody)