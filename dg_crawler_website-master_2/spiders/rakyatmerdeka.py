from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date
from copy import deepcopy

# author : 宋宇涛
class RakyatmerdekaSpider(BaseSpider):
    name = 'rakyatmerdeka'
    website_id = 22
    language_id = 1952
    start_urls = ['https://www.rakyatmerdeka.co.id/']

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@id="menu-menu-2"]/li/a')
        for category in categories:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./text()').get()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))
    def parse_page(self, response):
        flag = True
        articles = response.xpath("//ul[@class='penci-wrapper-data penci-grid']/li/article")
        meta = response.meta
        if self.time is not None:
            t = articles[-1].xpath('.//span[@class="otherl-date"]/time/text()').get().replace(',', '').split(" ")
            last_time = "{}-{}-{}".format(t[2], date.ENGLISH_MONTH[t[0]], t[1]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.xpath('.//span[@class="otherl-date"]/time/text()').get().replace(',', '').split(' ')
                pub_time = "{}-{}-{}".format(tt[2], date.ENGLISH_MONTH[tt[0]], tt[1]) + ' 00:00:00'
                article_url = article.xpath('.//h2/a/@href').get()
                title = article.xpath('.//h2/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath(
                    '//div[@class="penci-pagination align-left"]/ul/li').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath(
                    '//div[@class="penci-pagination align-left"]/ul/li')[-1]
                next_page=next_page.xpath(".//a/@href")
                yield Request(url=next_page.get(), callback=self.parse_page, meta=deepcopy(meta))
    def parse_item(self, response):
        item = NewsItem()
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//*[@id="penci-post-entry-inner"]')]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [response.xpath('//*[@id="main"]/div/article/div[@class="post-image"]/a/@href').get()]
        return item