from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date
from copy import deepcopy

# author:宋宇涛
class DetikSpider(BaseSpider):
    name = 'detik'
    website_id =126
    language_id =1952
    start_urls = ['https://news.detik.com/indeks']
    month = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }
    def parse(self, response):
        meta = response.meta
        categories = response.xpath('/html/body/div[4]/div[2]/div[1]/nav/ul/li[1]/a')
        for category in categories:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./div/text()').get()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))
    def parse_page(self, response):
        flag = True
        articles = response.xpath('//*[@id="indeks-container"]/article')
        meta = response.meta
        if self.time is not None:
            t = articles[-1].xpath('.//div[@class="media__date"]/span/@title').get().split()[1:-2]
            last_time = "{}-{}-{}".format(t[-1], self.month[t[1]], t[0]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.xpath('.//div[@class="media__date"]/span/@title').get().split()[1:-2]
                pub_time = "{}-{}-{}".format(tt[-1], self.month[tt[1]], tt[0]) + ' 00:00:00'
                article_url = article.xpath('.//h3[@class="media__title"]/a/@href').get()
                title = article.xpath('.//h3[@class="media__title"]/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath(
                    '/html/body/div[4]/div[2]/div[2]/div/div[2]/a[9]/@href') is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath(
                    '/html/body/div[4]/div[2]/div[2]/div/div[2]/a[9]/@href').get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))
    def parse_item(self, response):
        item = NewsItem()
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '/html/body/div[4]/div[2]/div[1]/article/div[5]/div[1]')]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [response.xpath('/html/body/div[4]/div[2]/div[1]/article/div[2]/figure/img/@src').get()]
        return item
