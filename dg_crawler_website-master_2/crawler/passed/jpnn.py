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
class JpnnSpider(BaseSpider):
    name = 'jpnn'
    website_id = 48
    language_id = 1952
    start_urls = ['https://www.jpnn.com/']
    myHeader = deepcopy(MOZILLA_HEADER)
    rePattern = r'[0-9]{1,2} [A-Z][a-z].*?:[0-9]{1,2}'

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//ul[@class="hz-rubrik"]//a')
        for category in categories[0: -4]:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./text()').get()
            meta['data'] = {'category1': category1, 'referer': page_link}
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta), headers=self.myHeader)

    def parse_page(self, response):
        flag = True
        meta = response.meta
        articles = response.xpath('//ul[@class="content-list"]/li/article')
        if self.time is not None:
            t = articles[-1].xpath('.//span[@class="silver"]/text()').get()
            t = re.findall(self.rePattern, str(t))[0].split(' ')
            last_time = "{}-{}-{}".format(t[2], month[t[1]], t[0]) + ' ' + t[-1] + ':00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.xpath('.//span[@class="silver"]/text()').get()
                tt = re.findall(self.rePattern, str(tt))[0].split(' ')
                pub_time = "{}-{}-{}".format(tt[2], month[tt[1]], tt[0]) + ' ' + tt[-1] + ':00'
                article_url = article.xpath('.//div[@class="content"]/h2/a/@href').get()
                title = article.xpath('.//div[@class="content"]/h2/a/text()').get()
                category2 = article.xpath('.//strong[@class="uppercase red"]/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                meta['data']['category2'] = category2
                meta['data']['article_url'] = article_url
                self.myHeader['referer'] = meta['data']['referer']
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta), headers=deepcopy(self.myHeader))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            current_page = response.xpath('//div[@class="pagination"]//li[@class="active"]/a/text()').get()
            if int(current_page) == 1:
                next_page = response.xpath('//div[@class="pagination"]/ul/li/a/@href')[-2].get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta), headers=self.myHeader)
            else:
                if response.xpath('//div[@class="pagination"]/ul/li/a/text()')[-1].get() != "Next":
                    self.logger.info("到达最后一页")
                else:
                    next_page = response.xpath('//div[@class="pagination"]/ul/li/a/@href')[-1].get()
                    yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta), headers=self.myHeader)

    def parse_item(self, response):
        item = NewsItem()
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = meta['data']['category2']
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join([paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath('//div[@itemprop="articleBody"]/p')]])
        if response.xpath('//div[@class="pagination"]/ul/li/a/text()').get():
            total_page = response.xpath('//div[@class="pagination"]/ul/li/a/text()')[-3].get()
            for i in range(2, int(total_page)+1):
                next_page = meta['data']['article_url'] + '?page=' + str(i)
                tree = etree.HTML(requests.get(url=next_page, headers=self.myHeader, timeout=100).text)
                text = "\n".join(["".join(text) for text in tree.xpath('//div[@itemprop="articleBody"]/p//text()')])
                item['body'] = item['body'] + '\n' + text
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = response.xpath('//*[@class="content-scroll"]/div[@class="page-content"]//img/@src').getall()
        return item
