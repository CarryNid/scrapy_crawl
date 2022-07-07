from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import scrapy

import re

# author: 张开林

class DapNewsSpider(BaseSpider):
    name = 'dapnews'
    website_id = 1879
    language_id = 1982


    # start_urls = ['https://dap-news.com/category/national','https://dap-news.com/category/international']

    start_urls = ['https://dap-news.com/category/national', 'https://dap-news.com/category/politic',
                  'https://dap-news.com/category/international', 'https://dap-news.com/category/scholar',
                  'https://dap-news.com/category/advertising', 'https://dap-news.com/category/specialedition',
                  'https://dap-news.com/category/qansuculture', 'https://dap-news.com/category/economic',
                  'https://dap-news.com/category/entertianment', 'https://dap-news.com/category/sport',
                  'https://dap-news.com/category/technology', 'https://dap-news.com/category/entrepreneur',
                  'https://dap-news.com/category/health']

    time = None
    item = NewsItem()



    def parse(self, response):
        for i in range(len(self.start_urls)):
            yield scrapy.Request(url=self.start_urls[i],callback=self.parseUnit)

    def parseUnit(self,response):
        num_page = response.xpath('//div[@class="pagination"]/span[1]/text()').extract()
        if len(num_page) != 0:
            num_page = int(num_page[0].split(' ')[-1])
        else:
            num_page = 1
        for page in range (1,num_page+1):
            url = response.url + 'page/' + str(page)
            yield scrapy.Request(url=url, callback=self.skipDetailed)

    def skipDetailed(self,response):
        news_collection = response.xpath('//li[@class="infinite-post"]/a[1]/@href').extract()
        for news_url in news_collection:
            pattern = '\d{4}\/\d{2}/\d{2}'
            pub_time = re.findall(pattern=pattern, string=news_url)[0]
            pub_time = pub_time.replace('/','-') + ' ' + '00:00:00'
            self.item['pub_time'] = pub_time
            if self.time == None or DateUtil.formate_time2time_stamp(pub_time) >= int(self.time):
                yield scrapy.Request(url=news_url, callback=self.parseDetailed)
            else:
                self.logger.info('Time Terminate!')
                break


    def parseDetailed(self,response):

        title = response.xpath('//h1[@class="post-title entry-title left"]/text()').extract()
        title = ''.join(title)

        url = str(response.url).replace('https://dap-news.com/','')
        index = url.find('/')
        category1 = url[:index]

        category2 = 'None'

        text = response.xpath('//div[@id="content-main"]/p/text()').extract()

        if len(text) != 0:
            body = ' '.join(text).replace('\xa0',' ').replace('\u200b','\n')
            abstract = ' '.join(text[0]).replace('\xa0',' ').replace('\u200b','\n')
        else:
            body = 'None'
            abstract = 'None'

        # 第1张图片可能是系统自动生成的，在每个网页均出现，所以删去
        images = response.xpath('//div[@id="content-area"]//img/@src').extract()
        images = images[1:]
        if len(images) == 0: images = 'None'

        self.item['title'] = title
        if category1 == 'entertianment': category1 = 'entertainment'
        # 这里原网站拼写错误

        self.item['category1'] = category1
        self.item['category2'] = category2
        self.item['body'] = body
        self.item['abstract'] = abstract
        # self.item['pub_time'] = pub_time
        self.item['images'] = images
        yield self.item