# encoding: utf-8
from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import time

# author：欧炎镁
class NTvdeSpider(BaseSpider):
    name = 'n_tvde'
    # allowed_domains = ['n-tv.de']
    start_urls = ['https://www.n-tv.de/thema/index-1-9']

    website_id = 1767
    language_id = 1846
    custom_settings = {'DOWNLOAD_TIMEOUT':60}
    proxy = '02'

    api = 'https://www.n-tv.de/thema/index-{}'  # 用于获取不同主题
    ascii_n = int(64)  # 主题ascii码，获取以A-Z开头的主题

    def parse(self, response):
        a_obj_list = response.css('div.theme__list a')
        for a_obj in a_obj_list:
            meta = {'data': {'category2':a_obj.css('::text').extract_first()}}
            page_link = a_obj.css('::attr(href)').extract_first()
            yield scrapy.Request(url=page_link,callback=self.parse_page,meta=deepcopy(meta))
        if self.ascii_n < 90:  # 获取以A-Z开头的主题
            self.ascii_n += 1
            yield scrapy.Request(url=self.api.format(chr(self.ascii_n)),callback=self.parse)

    def parse_page(self,response):
        article_obj_link = response.css('article.teaser.teaser--inline ')
        if article_obj_link: # 如果新闻列表有新闻
            flag = True
            if self.time is None:
                for article_obj in article_obj_link:
                    response.meta['data']['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(article_obj.css('span.teaser__date::text').extract_first().strip(), "%d.%m.%Y %H:%M"))
                    response.meta['data']['abstract'] = article_obj.css('p.teaser__text').xpath('string(.)').extract_first().strip()
                    item_link = article_obj.css('div.teaser__content a::attr(href)').extract_first()
                    yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(response.meta))
            else:
                last_pub = int(time.mktime(time.strptime(article_obj_link[-1].css('span.teaser__date::text').extract_first().strip(), "%d.%m.%Y %H:%M")))
                if self.time < last_pub:
                    for article_obj in article_obj_link:
                        response.meta['data']['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(article_obj.css('span.teaser__date::text').extract_first().strip(), "%d.%m.%Y %H:%M"))
                        response.meta['data']['abstract'] = article_obj.css('p.teaser__text').xpath('string(.)').extract_first().strip()
                        item_link = article_obj.css('div.teaser__content a::attr(href)').extract_first()
                        yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(response.meta))
                else:
                    self.logger.info("时间截止")
                    flag = False
            if flag:
                try:
                    next_page_link = response.css('a.paging__next1.icon.icon__arrow::attr(href)').extract_first()
                    yield scrapy.Request(next_page_link, callback=self.parse_page,meta=deepcopy(response.meta))
                except:
                    pass

    def parse_item(self,response):
        response.meta['data']['title'] = response.css('span.article__headline::text').extract_first()
        if response.meta['data']['title'] != 'Der Sport-Tag':
            response.meta['data']['category1'] = response.css('nav.breadcrumb span')[1].xpath('string(.)').extract_first()
            response.meta['data']['category2'] = ','.join(response.css('section.article__tags ul li a::text').extract()) if response.css('section.article__tags') else response.meta['data']['category2'] # 如果有多个类别就取多个类别
            response.meta['data']['images'] = response.css('article.article picture.media img::attr(data-src),article.article picture.media img::attr(src)').extract() if response.css('article.article picture.media img') else []
            response.meta['data']['body'] = '\n'.join([i.strip() for i in response.xpath('//div[@class="article__text"]/*[not(self::div)]').xpath('string(.)').extract()])
            if not response.meta['data']['abstract']:
                response.meta['data']['abstract'] = response.meta['data']['body'].split('.')[0] + '.' # 文章摘要   若没有则默认为文章第一句话
            item = NewsItem(response.meta['data'])
            yield item