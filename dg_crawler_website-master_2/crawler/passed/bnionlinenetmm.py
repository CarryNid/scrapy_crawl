from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date


# author : 武洪艳
class BnionlinenetmmSpider(BaseSpider):
    name = 'bnionlinenetmm'
    website_id = 1473
    language_id = 2065
    start_urls = ['http://www.bnionline.net/mm/']  # ['http://www.bnionline.net/mm/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#block-system-main-menu > ul > li')[2:5]
        for category in categories:
            category1 = category.select_one('li > a').text
            if category.select_one('li > a').get('href') == '/mm/feature':
                yield Request(url='https://www.bnionline.net' + category.select_one('li > a').get('href'), callback=self.parse_page,
                              meta={'category1': category1, 'category2': None})
            else:
                for i in category.select('li > ul > li > a'):
                    yield Request(url='https://www.bnionline.net' + i.get('href'), callback=self.parse_page,
                                  meta={'category1': category1, 'category2': i.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if self.time is not None:
            t = soup.select('#main-content span[datatype]')[-1].text.replace(',', ' ').split(' ')
            if len(t) == 1:
                last_time = t[0] + ' 00:00:00'
            else:
                last_time = "{}-{}-{}".format(t[3], date.ENGLISH_MONTH[t[0]], t[1]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            articles = soup.select('#main-content a')
            for i in articles:
                if (i.get('href').split(':')[0] == 'https'):
                    yield Request(url=i.get('href'), callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('#main-content a[title="Go to next page"]') == None:
                self.logger.info("no more pages")
            else:
                next_page = 'https://www.bnionline.net' + soup.select_one('#main-content a[title="Go to next page"]').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        if soup.select_one('article[id] div')!= None:
            item['title'] = soup.select_one('article[id] div').text
        if soup.select_one('article[id] span[datatype]') != None:
            tt = soup.select_one('article[id] span[datatype]').text.replace(',', ' ').split(' ')
            item['pub_time'] = "{}-{}-{}".format(tt[5], date.ENGLISH_MONTH[tt[2]], tt[3]) + ' 00:00:00'
        else:
            item['pub_time'] = DateUtil.time_now_formate()
        item['images'] = [img.get('src') for img in soup.select('article[id] img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('article[id] p') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
