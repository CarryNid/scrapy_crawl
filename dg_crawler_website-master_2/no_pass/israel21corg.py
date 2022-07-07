# encoding: utf-8
from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import time

# author：欧炎镁
class Israel21corgSpider(BaseSpider):
    name = 'israel21corg'
    allowed_domains = ['israel21c.org']
    start_urls = ['http://israel21c.org/']
    website_id = 1933
    language_id = 1866
    proxy = '02'

    def parse(self, response):
        a_obj_list = response.css('div.header-right ul li')
        for a_obj in a_obj_list[:-1]:
            meta = {'category1': a_obj.css('::text').extract_first()}
            page_link = a_obj.css('::attr(href)').extract_first()
            if 'http' not in page_link:
                page_link = 'http://israel21c.org' + page_link
            yield scrapy.Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        div_obj_list = response.css('section.cols4 article.item div.item-body')
        if div_obj_list:  # 如果新闻列表有新闻
            flag = True
            if self.time is None:
                for div_obj in div_obj_list:
                    response.meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(div_obj.css('div.date::text').extract_first().strip(),"%B %d, %Y, %I:%M %p")) if div_obj.css('div.date') else DateUtil.time_now_formate()
                    response.meta['title'] = div_obj.css('h1.headline a::text').extract_first()
                    response.meta['abstract'] = div_obj.css('h2.underline a::text').extract_first().strip() if div_obj.css('h2.underline') else None
                    item_link = div_obj.css('h1.headline a::attr(href)').extract_first()
                    yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(response.meta))
            else:
                lengths = len(div_obj_list)
                last_pub = self.time -1
                while lengths: # 如果最后一个没有时间，就拿倒数第二个新闻的时间
                    if div_obj_list[lengths-1].css('div.date'):
                        last_pub = int(time.mktime(time.strptime(div_obj_list[lengths-1].css('div.date::text').extract_first().strip(),"%B %d, %Y, %I:%M %p")))
                        break
                    else:
                        lengths -= 1
                if self.time < last_pub:
                    for div_obj in div_obj_list:
                        response.meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('div.date::text').extract_first().strip(), "%B %d, %Y, %I:%M %p"))
                        response.meta['title'] = div_obj.css('h1.headline a::text').extract_first()
                        response.meta['abstract'] = div_obj.css('h2.underline a::text').extract_first().strip() if div_obj.css('h2.underline') else None
                        item_link = div_obj.css('h1.headline a::attr(href)').extract_first()
                        yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(response.meta))
                else:
                    self.logger.info("时间截止")
                    flag = False
            if flag:
                try:
                    next_page_link = response.css('div.wp_page_numbers ul li.active_page + li a::attr(href)').extract_first()
                    yield scrapy.Request(next_page_link, callback=self.parse_page, meta=deepcopy(response.meta))
                except:
                    pass

    def parse_item(self, response):
        item=NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join([i.strip() for i in response.css('div.article-body  >*:not(div)').xpath('string(.)').extract() if i.strip() != ''])
        item['images'] = response.css('div.media.article-media img,div.wp-caption img').css('::attr(src)').extract()
        item['abstract'] = item['body'].split('\n')[0] if ((not response.meta['abstract']) and item['body']) else response.meta['abstract']
        yield item
