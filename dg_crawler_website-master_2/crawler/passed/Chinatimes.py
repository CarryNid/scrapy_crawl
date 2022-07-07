# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author: 王晋麟
class ChinatimesSpider(BaseSpider):
    name = 'Chinatimes'
    website_id = 910
    language_id = 1814
    types = ['opinion', 'star', 'life', 'money', 'world', 'chinese', 'society', 'sports']
    start_urls = ['https://www.chinatimes.com/' + str(type) + '/total?chdtv' for type in types]

    def parse(self, response):
        news_hrefs = response.xpath('/html/body/div[2]/div/div[2]/div/section/ul//*[@class="title"]/a/@href').extract()
        for news_href in news_hrefs:
            news_url = 'https://www.chinatimes.com' + news_href + '?chdtv'
            category = news_href.split('/')[1]
            yield Request(url=news_url, callback=self.parse_item, meta={'category': category})
        Nextpage_li_class = response.xpath('//ul[@class="pagination"]/li/@class').extract()[-2]
        if Nextpage_li_class != 'page-item disabled':
            Nextpage_url = 'https://www.chinatimes.com' + response.xpath('//ul[@class="pagination"]//@href').extract()[-2] + '&chdtv'
            yield Request(url=Nextpage_url, callback=self.parse)

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.xpath('//*[@class="article-title"]/text()').extract()
        item['category1'] = 'news'
        item['category2'] = response.meta['category']
        ps = response.xpath('//*[@itemprop="articleBody"]/p/text()').extract()
        body = ''
        for p in ps:
            body += p
        item['body'] = body
        item['abstract'] = list(body.split('。'))[0]
        item['pub_time'] = response.xpath('//*[@class="meta-info-wrapper"]/div/time/@datetime').extract()
        try:
            item['images'] = response.xpath('//*[@id="page-top"]/div/div[2]/div/div/article/div/div[1]/div[1]/figure/div/img/@src').extract()
        except:
            item['images'] = None
        yield item
