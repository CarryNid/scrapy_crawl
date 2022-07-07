# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from utils.date_util import DateUtil
import re

# author : 赖晓杰

class DemoSpiderSpider(BaseSpider):
    name = 'gxzf'
    website_id = 1888
    language_id = 1813
    start_urls = ['http://www.gxzf.gov.cn/']
    is_http = 1


    def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        category = soup.select('ul.tab-index-nav > li > a')[0]
        meta = {'category1': category.text}
        t = soup.select('ul.tab-index-nav > li > a')[0]['href']
        url = 'http://www.gxzf.gov.cn' + t[1:]
        yield Request(url=url, callback=self.t_parse, meta=meta)

    def t_parse(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        lst = []
        s = soup.select('div.more-page > script')[0].text
        last = int(s[s.index('(') + 1:s.index(',')])
        lst.append('http://www.gxzf.gov.cn/gxyw/index.shtml')
        for i in range(1, last):
            lst.append('http://www.gxzf.gov.cn/gxyw/index_{}'.format(i) + '.shtml')
        for url in lst:
            yield Request(url=url, callback=self.parse2, meta=response.meta)

    def parse2(self,response):
        soup = BeautifulSoup(response.text,'lxml')
        time_ = []
        for t in soup.select('ul.more-list > li > span'):
            time_.append(t.text[1:11])
        index = 0
        for item in soup.select('ul.more-list > li > a'):
            detial_url = 'http://www.gxzf.gov.cn/gxyw' + item['href'][1:]

            if self.time == None or DateUtil.formate_time2time_stamp(time_[index]+' 00:00:00') >= int(self.time):
                index += 1
                yield Request(url=detial_url, callback=self.parse3, meta=response.meta)
            else:
                self.logger.info("时间截止")
                break

    def parse3(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['title'] = soup.select('div.article-left > div.article > h1')[0].text
        item['category1'] = response.meta['category1']
        if soup.find('div', class_ = "view TRS_UEDITOR trs_paper_default") != None:
            item['body'] = ''
            item['abstract'] = ''
        else:
            content = soup.select('div.article-con')[0].text
            content = content.replace('\n', '')
            item['body'] = content
            item['abstract'] = content[:content.index('。') + 1]

        s = soup.select('div.article > div > div.article-inf-left')[0].text
        item['pub_time'] = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", s).group() + ':00'

        img = soup.select('div.article-con > div > p')
        for i in img:
            if i.find('img') != None:
                item['images'] = ['http://www.gxzf.gov.cn/gxyw' + i.find('img')['src'][1:], ]

        yield item
