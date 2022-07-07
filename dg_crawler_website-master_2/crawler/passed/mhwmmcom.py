from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date
import re


class MhwmmcomSpider(BaseSpider):
    name = 'mhwmmcom'
    website_id = 290
    language_id = 1813
    # allowed_domains = ['www.mhwmm.com']
    start_urls = ['https://www.mhwmm.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('div.nav.clearfix > div.top_nav > div > ul > li a')[1:]
        for category in categories:
            yield Request(url='https://www.mhwmm.com/' + category.get('href'), callback=self.parse_page,
                          meta={'category1': category.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.leftnewslist > div.leftnews.clearfix > ul > li')
        if self.time is not None:
            t = re.split(r"[年 月 日]", articles[-1].select_one('.btm.clearfix > div.time.fl').text.split('：')[1])
            last_time = "{}-{}-{}".format(t[0], t[1], t[2]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = re.split(r"[年 月 日]", article.select_one('.btm.clearfix > div.time.fl').text.split('：')[1])
                pub_time = "{}-{}-{}".format(tt[0], tt[1], tt[2]) + ' 00:00:00'
                article_url = 'https://www.mhwmm.com/' + article.select_one('li > a').get('href')
                title = article.select_one('.tit > a').text
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': response.meta['category1'], 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select('div.leftnews.clearfix .pagecode a')[-1].get('href') is None:
                self.logger.info("no more pages")
            else:
                next_page = 'https://www.mhwmm.com/' + soup.select('div.leftnews.clearfix .pagecode a')[-1].get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = ['https://www.mhwmm.com/' + img.get('src') for img in soup.select('.article_cont img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('.article_cont') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
