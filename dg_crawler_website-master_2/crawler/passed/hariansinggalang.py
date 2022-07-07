from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date
from copy import deepcopy

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
class HariansinggalangSpider(BaseSpider):
    name = 'hariansinggalang'
    website_id = 72
    language_id = 1952
    start_urls = ['https://hariansinggalang.co.id/']

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@class="jeg_header_wrapper"]//*[@class="jeg_mainmenu_wrap"]/ul/li//a')
        for category in categories[1: -2]:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./text()').get()
            if page_link != "#":
                meta['data'] = {
                    'category1': category1
                }
                yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        articles = response.xpath('//div[@class="jeg_posts jeg_load_more_flag"]/article')
        meta = response.meta
        #  Selasa, 25 Januari 2022 | 16:58
        if self.time is not None:
            t = articles[-1].xpath('.//*[@class="jeg_meta_date"]//text()').get().strip().split(' ')
            last_time = "{}-{}-{}".format(t[3], month[t[2]], t[1]) + ' ' + t[-1] + ':00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.xpath('.//*[@class="jeg_meta_date"]//text()').get().strip().split(' ')
                pub_time = "{}-{}-{}".format(tt[3], month[tt[2]], tt[1]) + ' ' + tt[-1] + ':00'
                article_url = article.xpath('.//h3[@class="jeg_post_title"]/a/@href').get()
                title = article.xpath('.//h3[@class="jeg_post_title"]/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//a[@class="page_nav next"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath('//a[@class="page_nav next"]/@href').get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem()
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        # item['body'] = '\n'.join(
        #     [paragraph.strip() for paragraph in response.xpath('//div[@class="content-inner "]/p//text()').getall()]
        # )
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//div[@class="content-inner "]/p | //div[@class="content-inner "]/div')] if paragraph.strip() != '' and paragraph.strip() != '\xa0']
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [response.xpath('//*[@class="jeg_featured featured_image"]/a/@href').get()]
        return item
