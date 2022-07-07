from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


# author : 梁智霖
#check:why
class Bbc_thaiSpider(BaseSpider):
    name = 'bbc_thai'
    website_id = 1586
    language_id = 2208
    #allowed_domains = ['bbc.com']
    start_urls = ['https://www.bbc.com/thai']
    # is_http = 1
    #若网站使用的是http协议，需要加上这个类成员(类变量)
    proxy = '02' #这个网站会反爬

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.bbc-bjn8wh.eg26bel0 > div > ul >li > a')[1:5]
        for category1 in categories:
            category_url = 'https://www.bbc.com/' + category1.get('href')
            yield Request(url=category_url, callback=self.parse_page, meta={'category1': category1.text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        if self.time is not None:
            last_time = soup.select('div.bbc-1mtos2m.e3hd7yi0 > time')[-1].get('datetime') + " 00:00:00"
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            articles = soup.select('div.bbc-1mtos2m.e3hd7yi0 > h2 > a')
            for article in articles:
                article_url = article.get('href')
                title = article.text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'],'title': title})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            try:
                if soup.select('#pagination-next-page > span')[0].text == "ถัดไป":
                    next_page = response.url.split('?page=')[0] + soup.select('nav > span > a')[-1].get('href')
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            except:
                self.logger.info(response.url + ' has no the next page.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('main > div > p') + soup.select('div.e1gggypo0.bbc-oa9drk.essoxwk0 > ul > li> a')
             if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [img.get('src') for img in soup.select('div > div > picture > img')]
        pub_time = soup.select_one('main > div > time').get('datetime') + " 00:00:00"
        item['pub_time'] = pub_time
        yield item