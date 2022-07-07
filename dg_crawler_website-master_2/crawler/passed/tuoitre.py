import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
from crawler.spiders import BaseSpider

from crawler.items import *
from utils.date_util import DateUtil

#author:马嘉颖
class tuoitreSpider(BaseSpider):
    name = 'tuoitre'
    website_id = 251  # 网站的id(必填)
    language_id = 2242 # 所用语言的id
    start_urls = ['https://tuoitre.vn/']
    # allowed_domains = ['tuoitre.vn']


    def parse(self,response):
        catagory=response.xpath("//ul[@class='menu-ul']/li/a")
        for i in catagory[1:]:
            if i.xpath("./@data-id"):
                yield Request(url="https://tuoitre.vn/timeline/"+i.xpath("./@data-id").extract()[0]+"/trang-1.htm",callback=self.parse2,meta={"category1":i.xpath("./text()").extract()[0]})
        pass

    def parse2(self, response):
        if response.xpath("//body/li"):
            articles = response.xpath("//body/li")
            for i in articles:
                time0 = time.strptime(i.xpath("./@data-newsid").extract()[0].strip()[:8], "%Y%m%d")
                time1 = time.mktime(time0)
                if self.time is None or int(time1) >= int(self.time):
                    yield Request(url="https://tuoitre.vn" + i.xpath("./a[1]/@href").extract()[0],
                                  callback=self.parse3,meta={"category1":response.meta["category1"]})
            yield Request(
                url=response.url.replace("trang-" + str(response.meta['depth']), "trang-" + str(response.meta['depth'] + 1)),
                callback=self.parse2, meta={"category1":response.meta["category1"]})
        else:
            return


    def parse3(self,response):
        # print(response)
        item=NewsItem()
        if(response.xpath("//h1/text()")):
            item['title']=response.xpath("//h1/text()").extract()[0]
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['body'] = "".join(response.xpath("//div[@class='content fck']/p").xpath("string(.)").extract())
        if(response.xpath("//h2/text()")):
            item['abstract'] = response.xpath("//h2/text()").extract()[0].strip()
        try:
            item['pub_time'] = time.strptime(response.xpath("//div[@class='date-time']/text()").extract()[0].strip(), '%d/%m/%Y %H:%M GMT+7')
        except:
            item['pub_time'] = DateUtil.time_now_formate()
        item['images'] = response.xpath("//div[@class='content fck']//img/@src").extract()
        yield item
