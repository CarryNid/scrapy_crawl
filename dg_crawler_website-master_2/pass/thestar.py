# encoding: utf-8
from bs4 import BeautifulSoup

import common.date
import utils
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


#Author:陈卓玮
# check: 凌敏 pass
class thestarSpider(BaseSpider):
    name = 'thestar'
    website_id = 150
    language_id = 1866
    start_urls = ['https://www.thestar.com.my/news/latest']

    def time_parser(self,oral_time):
        if 'ago' in oral_time and 'd' not in oral_time:
            return utils.date_util.DateUtil.time_now_formate()
        elif 'ago' in oral_time and 'd' in oral_time:
            day = int(oral_time.split('d')[0])
            return utils.date_util.DateUtil.time_stamp2formate_time(utils.date_util.DateUtil.time_ago(day=day))
        else:
            time = oral_time.split(' ')
            time[2], time[0] = time[0], time[2]
            time[1] = str(common.date.ENGLISH_MONTH[time[1]])
            return '-'.join(time)+' 00:00:00'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        for i in soup.select("#nav-tabs-wrapper li a"):
            co_url = ("https://www.thestar.com.my" + i.get('href'))
            yield Request(url = co_url,callback=self.parse2)

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        time_oral = utils.date_util.DateUtil.time_now_formate()
        for i in soup.select('.timeline > .row'):
            time_oral = (i.select_one('time').text)
            category1 = (i.select_one('.kicker').text)
            title = (i.select_one('h2').text.strip())
            essay_url = (i.select_one('h2 a').get('href'))
            yield Request(url = essay_url,callback=self.essay_parser,
                          meta={'oral_time':time_oral,
                                'category1':category1,
                                'title':title})

##翻页
        page_list = (soup.select('.pager .pager-nav a'))
        current_page_index = page_list.index((soup.select_one('.pager .active a')))
        max_page = page_list[-2]
        if int(max_page.text) > current_page_index:
            next_page_url = page_list[current_page_index + 1].get('href')
            time_stamp = utils.date_util.DateUtil.formate_time2time_stamp(self.time_parser(time_oral))
            if self.time == None or time_stamp >= self.time:
                yield Request(url = next_page_url,callback=self.parse2)

    def essay_parser(self,response):
        soup = BeautifulSoup(response.text, 'lxml')

        body = ''
        for i in soup.select('#story-body p'):
            body += (i.text.strip()) + '\n'

        img = []
        for i in soup.select('img'):
            img.append(i.get('src'))

        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        item['pub_time'] = self.time_parser(response.meta['oral_time'])
        item['images'] = img
        yield item


