from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date
from copy import deepcopy


# author : 宋宇涛
class EriaSpider(BaseSpider):

    start_urls = ['https://www.eria.org/news-and-views']
    name = 'eria'
    website_id = 693
    language_id = 1866
    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@id="frm_search_research"]/div/ul//a')[1:]
        for category in categories:
            page_link = "https://www.eria.org"+category.xpath('./@href').get()
            category1 = category.xpath('./text()').get()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))
    def parse_page(self, response):
        flag = True
        articles = response.xpath('//*[@id="main-content"]/div[2]/div/article/section/div/div')
        meta = response.meta
        if self.time is not None:
            t = articles[-1].xpath('.//p[@class="posted-date"]/text()').get().split()
            last_time = "{}-{}-{}".format(t[2], date.ENGLISH_MONTH[t[1]], t[0]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.xpath('.//p[@class="posted-date"]/text()').get().split()
                pub_time = "{}-{}-{}".format(tt[2], date.ENGLISH_MONTH[tt[1]], tt[0]) + ' 00:00:00'
                article_url = "https://www.eria.org"+article.xpath('./figure/a/@href').get()
                title = article.xpath('.//h2/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            #
            if response.xpath(
                    '//*[@id="main-content"]/div[2]/div/article/div[3]/a[5]').get() is None:
                self.logger.info("到达最后一页")
            else:
                page = int(response.xpath('//*[@id="main-content"]/div[2]/div/article/div[3]/span/text()').get())
                page+=1
                next_page = "https://www.eria.org"+response.xpath(
                    '//*[@id="main-content"]/div[2]/div/article/div[3]/a[5]/@href').get().split('?')[0]
                next_page=next_page+f"?sort=date-desc&start_rec={page*10-10}&page_size=10"
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
                '//*[@id="main-content"]/div[2]/div/article/div/p')[1:]]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = ["https://www.eria.org"+response.xpath('//*[@id="main-content"]/div[2]/div/article/div/p[1]/img/@src').get()]
        return item