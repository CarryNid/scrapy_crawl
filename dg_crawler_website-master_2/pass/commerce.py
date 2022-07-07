from crawler.spiders import BaseSpider
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http.request import Request

# author: 蔡卓妍
from utils.date_util import DateUtil


class CommerceSpider(BaseSpider):
    name = 'commerce'
    website_id = 1360
    language_id = 1797
    start_urls = ['https://www.commerce.gov.mm']

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        new_url = soup.select('#region-content .block.block-views')
        for i in new_url:
            news_url = 'https://www.commerce.gov.mm/' + i.select_one('div.view-header > p > span > a').get('href')
            category1 = i.select_one('h2').text
            meta = {'category1':category1}
            yield Request(url=news_url,meta=meta,callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.view-content .views-row')
        for i in articles:
            article = 'https://www.commerce.gov.mm' + i.select_one('.views-field-title > span > a').get('href')
            response.meta['title'] = i.select_one('.views-field-title > span > a').text
            try:
                response.meta['abstract'] = i.select_one('.views-field-body p').text
            except:
                response.meta['abstract'] = response.meta['title']
            yield Request(url=article,meta=response.meta,callback=self.parse_item)
        if soup.find(title='Go to next page') != None:
            next_page = 'https://www.commerce.gov.mm' + soup.find(title='Go to next page').get('href')
            yield Request(url=next_page,callback=self.parse_page,meta=response.meta)
        else:
            self.logger.info("no more pages")

    def parse_item(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        try:
            item['body'] = "\n".join(i.text.strip() for i in soup.select('.field-type-text-with-summary p'))
        except:
            item['body'] = 'none'
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = DateUtil.time_now_formate()
        try:
            item['images'] = ['https:' + soup.select_one('.field-type-image a').get('href')]
        except:
            item['images'] = []
        yield item





