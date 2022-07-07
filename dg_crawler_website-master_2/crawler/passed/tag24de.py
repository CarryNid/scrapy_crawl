# encoding: utf-8
from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import time
import datetime
import requests
from requests.adapters import HTTPAdapter

# author：欧炎镁
class Tag24deSpider(BaseSpider):
    name = 'tag24de'
    # allowed_domains = ['tag24.de']
    start_urls = ['https://www.tag24.de/a-bis-z/1','https://www.tag24.de/a-bis-z/2','https://www.tag24.de/a-bis-z/3']

    website_id = 1764
    language_id = 1846
    custom_settings = {'DOWNLOAD_TIMEOUT': 60}
    proxy = '02'

    tz = datetime.timezone(datetime.timedelta(hours=+8)) # 用于将时间转成东八时区
    api = 'https://www.tag24.de/a-bis-z/{}'  # 用于获取不同主题
    ascii_n = int(96)  # 主题ascii码，获取以a-z开头的主题

    def parse(self, response):
        article_obj_list = response.css('article.article-tile')
        for article_obj in article_obj_list:
            meta = {'category1': article_obj.css('span.article-tile__headline').xpath('string(.)').extract_first()}
            page_link = article_obj.css('span a::attr(href)').extract_first()
            yield scrapy.Request(url=page_link,callback=self.parse_page,meta=deepcopy(meta))
        if self.ascii_n < 122:  # 获取以a-z开头的主题
            self.ascii_n += 1
            yield scrapy.Request(url=self.api.format(chr(self.ascii_n)),callback=self.parse)

    def parse_page(self, response):
        item_link_list = response.css('article.article-tile span a::attr(href)').extract()
        if item_link_list:
            flag = True
            if self.time is None:
                for item_link in item_link_list:
                    yield scrapy.Request(url=item_link,callback=self.parse_item,meta=deepcopy(response.meta))
            else:
                lengths = len(item_link_list) - 1 # item_link_list最后一个可能不是新闻详细页，可能是新闻列表，如果是新闻列表，就会报错，然后拿倒数第二个，最后一个网址如果五次都拿不到也拿倒数第二个
                while True:
                    try:
                        s = requests.session()
                        s.mount('https://', HTTPAdapter(max_retries=2)) # 重试5次
                        # response_item = s.get(url=item_link_list[lengths], timeout=60, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"},proxies={'https': 'http://192.168.235.5:8888'})
                        response_item = s.get(url=item_link_list[lengths], timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"})

                        last_pub = int(time.mktime(datetime.datetime.strptime(scrapy.Selector(response_item).css('div.article__info time::attr(datetime)').extract_first(),'%Y-%m-%dT%H:%M:%S%z').astimezone(self.tz).timetuple()))

                        break
                    except:
                        lengths -= 1
                if self.time < last_pub:
                    for item_link in item_link_list:
                        yield scrapy.Request(url=item_link, callback=self.parse_item,meta=deepcopy(response.meta))
                else:
                    self.logger.info("时间截止")
                    flag = False
            if flag:
                page_link = response.css('a.pagination__item.pagination__item--active + a::attr(href)').extract_first() # 如果最后一页就会是None
                if page_link:
                    yield scrapy.Request(page_link,callback= self.parse_page,meta=deepcopy(response.meta))

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.css('h2.article__headline1.content-h1::text').extract_first()
        if item['title']: # 排除主题页面
            item['abstract'] = response.xpath('//div[@class="article__paragraph"]/*[not(self::figure)][not(self::div)]|//h3[@class="content-h3"]')[0].xpath('string(.)').extract()
            item['pub_time'] = str(datetime.datetime.strptime(response.css('div.article__info time::attr(datetime)').extract_first().strip(),'%Y-%m-%dT%H:%M:%S%z').astimezone(self.tz))[:-6]
            item['body'] = '\n'.join([i.strip() for i in response.xpath('//div[@class="article__paragraph"]/*[not(self::figure)][not(self::div)]|//h3[@class="content-h3"]')[1:].xpath('string(.)').extract()])
            item['images'] = response.css('img.article__img::attr(src)').extract()
            item['category1'] = response.meta['category1']
            category = response.css('nav.breadcrumbs-nav ul li a::text').extract()
            if category:
                if category[0].strip() in ['Thema', 'Nachrichten']:# 如果第一个标签是Thema 则第二个是第一类别，第三个是第二类别
                    category.pop(0)
                item['category1'] = category[0].strip() if len(category) > 0 else response.meta['category1']
                item['category2'] = category[1].strip() if len(category) > 1 else None # 如果有第二个标签可以取到，就是第二类别
            yield item