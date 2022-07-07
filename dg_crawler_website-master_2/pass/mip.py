# encoding: utf-8
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from crawler.items import *
from crawler.spiders import BaseSpider
from utils.date_util import DateUtil
# author: 蔡卓妍

class MipSpider(BaseSpider):
    name = 'mip'
    website_id = 1357
    language_id = 1797
    start_urls = ['http://www.mip.gov.mm']
    is_http = 1  # 网站使用的是http协议， 需要加上这个类成员（类变量）

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        lists = [soup.select_one("#menu-item-257 > a")] + [soup.select_one("#menu-item-386 > a")]
        for i in lists:
            news_url = i.get("href")
            meta = {'category1': i.text}
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
        item['body'] = "\n".join(i.text.strip() for i in soup.select('.contentarea >p'))
        item['abstract'] = response.meta['title']
        item['images'] = response.meta['images']
        item['pub_time'] = DateUtil.time_now_formate()
        yield item