# encoding: utf-8
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from crawler.items import *
from crawler.spiders import BaseSpider
from utils import Burmese_time

# author: 蔡卓妍
from utils.date_util import DateUtil


class MipSpider(BaseSpider):
    name = 'mip'
    website_id = 1357
    language_id = 1797
    start_urls = ['http://www.mip.gov.mm']
    is_http = 1  # 网站使用的是http协议， 需要加上这个类成员（类变量）

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        news_url = soup.select_one('#menu-item-257 > a').get('href')
        # print('aaaa',news_url)  # 可以使用这种打印的方式，判断出错的地方在哪里
        meta = {'category1': soup.select_one('#menu-item-257 > a').text}
        yield Request(url=news_url,meta=meta,callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.fl-container.span12 > div > div > div > div > div.span12 > div')
        for article in articles:
            article_url = article.select_one(".blogpost_title").get('href')
            response.meta['images'] = [article.select_one('img').get('src')]
            response.meta['title'] = article.select_one('a').text
            yield Request(url=article_url,meta=response.meta,callback=self.parse_item)
        for i in soup.select('.pagerblock a')[1:]:# 翻页：网页内没有下一页选择键
            page = i.get('href')
            yield Request(url=page, meta=response.meta, callback=self.parse_page)

    def parse_item(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = 'None'
        item['body'] = "\n".join(i.text.strip() for i in soup.select('.contentarea >p')[2:])
        item['abstract'] = response.meta['title']
        item['images'] = response.meta['images']
        try:
            date = soup.select('.contentarea >p')[1].text.split()
            date2 = soup.select('.contentarea >p')[2].text.split()
            if (date[1] + 'လ') in Burmese_time.months:
                months = Burmese_time.months.index(date[1] + 'လ') + 1
            elif (date2[1] + 'လ') in Burmese_time.months:
                months = Burmese_time.months.index(date2[1] + 'လ') + 1
                date = date2
            else:
                months = Burmese_time.months.index(date[1]) + 1
            if months < 10:
                months = f'0{months}'
            if len(date[2]) == 2:
                day = Burmese_time.figure.index(date[2][0]) * 10 + Burmese_time.figure.index(date[2][1])
                item['pub_time'] = f'2021-{months}-{day} 00:00:00'
            else:
                day = Burmese_time.figure.index(date[2])
                item['pub_time'] = f'2021-{months}-0{day} 00:00:00'
        except:
            item['pub_time'] = DateUtil.time_now_formate()
        yield item