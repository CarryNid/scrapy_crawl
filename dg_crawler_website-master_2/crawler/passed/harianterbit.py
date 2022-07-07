from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from copy import deepcopy
from common.header import MOZILLA_HEADER
import re
import requests
from lxml import etree

# 部分月份的英文不同
month = {
    'Januari': 1,
    'Februari': 2,
    'Maret': 3,
    'April': 4,
    'Mei': 5,
    'Juni': 6,
    'Juli': 7,
    'Agustus': 8,
    'September': 9,
    'Oktober': 10,
    'November': 11,
    'Desember': 12
}


# author : 彭雨胜
class HarianterbitSpider(BaseSpider):
    name = 'harianterbit'
    website_id = 44
    language_id = 1952
    start_urls = ['https://harianterbit.com/']
    myHeader = deepcopy(MOZILLA_HEADER)
    rePattern = r'[0-9]{1,2} [A-Z][a-z].*?:[0-9]{1,2}'

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@class="nav__wrap"]/li/a')
        for category in categories[: -2]:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./text()').get()
            meta['data'] = {'category1': category1, 'referer': page_link}
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta), headers=self.myHeader)

    def parse_page(self, response):
        flag = True
        meta = response.meta
        articles = response.xpath('//div[@class="latest__item"]')
        if self.time is not None:
            t = articles[-1].xpath('.//date[@class="latest__date"]/text()').get()
            t = re.findall(self.rePattern, t)[0].split(' ')
            last_time = "{}-{}-{}".format(t[2], month[t[1]], t[0]) + ' ' + t[-1] + ':00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.xpath('.//date[@class="latest__date"]/text()').get()
                tt = re.findall(self.rePattern, tt)[0].split(' ')
                pub_time = "{}-{}-{}".format(tt[2], month[tt[1]], tt[0]) + ' ' + tt[-1] + ':00'
                article_url = article.xpath('.//h2[@class="latest__title"]/a/@href').get()
                title = article.xpath('.//h2[@class="latest__title"]/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                meta['data']['article_url'] = article_url
                self.myHeader['referer'] = meta['data']['referer']
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta), headers=deepcopy(self.myHeader))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//a[@class="paging__link paging__link--next"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = meta['data']['referer'] + response.xpath('//a[@class="paging__link paging__link--next"]/@href').get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta), headers=self.myHeader)

    def parse_item(self, response):
        item = NewsItem()
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['images'] = response.xpath('//*[@class="photo__img"]//img/@src').getall()
        item['body'] = '\n'.join([paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath('//*[@class="read__content clearfix"]/div | //*[@class="read__content clearfix"]/p')] if paragraph.strip().replace(' ', '') != ''])
        if response.xpath('//div[@class="paging__item"]/a/text()').get():
            total_page = response.xpath('//div[@class="paging__item"]/a/text()')[-2].get()
            for i in range(2, int(total_page)+1):
                next_page = meta['data']['article_url'] + '?page=' + str(i)
                tree = etree.HTML(requests.get(url=next_page, headers=self.myHeader, timeout=10).text)
                text = "\n".join(["".join(text) for text in tree.xpath('//*[@class="read__content clearfix"]/div//text() | //*[@class="read__content clearfix"]/p//text()')])
                item['body'] = item['body'] + '\n' + text
        item['abstract'] = item['body'].split('\n')[0]
        return item
