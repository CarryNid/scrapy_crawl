# encoding: utf-8


import scrapy
from scrapy import Request
import re
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

#author : 沈腾

month = {
            'មករា': '01',
            'កុម្ភៈ': '02',
            'មីនា': '03',
            'មេសា': '04',
            'ឧសភា': '05',
            'មិថុនា': '06',
            'កក្កដា': '07',
            'សីហា': '08',
            'កញ្ញា': '09',
            'តុលា': '10',
            'វិច្ឆិកា': '11',
            'ធ្នូ': '12'
        }

class Khmer7newsSpider(BaseSpider):
    name = 'khmer7news'
    website_id = 1877
    language_id = 1982
    start_urls = ['https://khmer7news.com/']
    '''
    由于网站url中包含柬埔寨语，举个例子这个网站“https://khmer7news.com/archives/category/ព័ត៌មានជាតិ”而传入解析过程中会变成
    “https://khmer7news.com/archives/category/%e1%9e%9f%e1%9f%81%e1%9e%8a%e1%9f%92%e1%9e%8b%e1%9e%80%e1%9e%b7%e1%9e%85%e1%9f%92%e1%9e%85”
    的网站，而传入有这些后面的参数的网站scrapy识别不出，因此手动上传了具体的url
    '''
    def parse(self, response):
        for i in range(1,586):#i值应该由时间推移而改变，目前更新到第580页，持续更新
            meta = {'category1':"ព័ត៌មានជាតិ"}
            yield Request(url="https://khmer7news.com/archives/category/ព័ត៌មានជាតិ/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,145):#i值应该由时间推移而改变，目前更新到第145页，持续更新
            meta = {'category1': "អន្តរជាតិ"}
            yield Request(url="https://khmer7news.com/archives/category/អន្តរជាតិ/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,39):#i值应该由时间推移而改变，目前更新到第39页，持续更新
            meta = {'category1': "សេដ្ឋកិច្ច"}
            yield Request(url="https://khmer7news.com/archives/category/សេដ្ឋកិច្ច/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,31):#i值应该由时间推移而改变，目前更新到第31页，持续更新
            meta = {'category1': "ជីវិតកម្សាន្ត"}
            yield Request(url="https://khmer7news.com/archives/category/ជីវិតកម្សាន្ត/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,6):#i值应该由时间推移而改变，目前更新到第6页，持续更新
            meta = {'category1': "កីឡា"}
            yield Request(url="https://khmer7news.com/archives/category/កីឡា/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,10):#i值应该由时间推移而改变，目前更新到第10页，持续更新
            meta = {'category1': "វប្បធម៌"}
            yield Request(url="https://khmer7news.com/archives/category/វប្បធម៌/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,5):#i值应该由时间推移而改变，目前更新到第5页，持续更新
            meta = {'category1':"បច្ចេកវិទ្យា"}
            yield Request(url="https://khmer7news.com/archives/category/បច្ចេកវិទ្យា/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,3):#i值应该由时间推移而改变，目前更新到第3页，持续更新
            meta = {'category1':"សុខភាព"}
            yield Request(url="https://khmer7news.com/archives/category/សុខភាព/page/%d" % i,
                          callback=self.parse_page, meta=meta)
        for i in range(1,91):#i值应该由时间推移而改变，目前更新到第91页，持续更新
            meta = {'category1':"សន្តិសុខសង្គម"}
            yield Request(url="https://khmer7news.com/archives/category/សន្តិសុខសង្គម/page/%d" % i,
                          callback=self.parse_page, meta=meta)
    # 网页抓取显示的时间为这种格式:ពុធ, 19 មករា 2022 9:26 ព្រឹក

    def parse_page(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        sj = soup.select('div.post-meta > span.date.meta-item > span:nth-child(2)')[-1].text.split(' ')
        # for s in ti:
        if self.time is not None:
            # s = s.text
            # sj = s.split(' ')
            sj[2] = month[sj[2]]
            last_time = str(sj[3]) + '-' + str(sj[2]) + '-' + str(sj[1]) + ' ' + str(sj[4]).rjust(5,'0') + ':00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.select('div.post-details > h3 > a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = soup.select_one('#the-post > header > div > h1').text
        ti = soup.select_one('#the-post > header > div > div > span > span:nth-child(2)')
        s = ti.text
        sj = s.split(' ')
        sj[2] = month[sj[2]]
        tim = str(sj[3]) + '-' + str(sj[2]) + '-' + str(sj[1]) + ' ' + str(sj[4]).rjust(5, '0') + ':00'
        item['pub_time'] = tim
        images = [i.get('src') for i in soup.select('#the-post > div.entry-content.entry.clearfix img')]
        item['images'] = images
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('#the-post > div.entry-content.entry.clearfix p')])
        item['abstract'] = item['body'].split('\n')[0]
        yield item


