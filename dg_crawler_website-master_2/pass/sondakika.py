from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date


# author : 梁智霖
class SondakikaSpider(BaseSpider):
    name = 'sondakika'
    website_id = 1839
    language_id = 2227
    allowed_domains = ['sondakika.com']
    start_urls = ['https://sondakika.com/']
    # is_http = 1
    #若网站使用的是http协议，需要加上这个类成员(类变量)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find(id='header-container').select('li > a')[1:5]
        for category1 in categories:
            category_url = 'https://www.sondakika.com' + category1.get('href')
            yield Request(url=category_url, callback=self.parse_page, meta={'category1': category1.text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('#main.fl > ul >li')

        if self.time is not None:
            t = articles[-1].select_one('span.hour.data_calc').get('title').split()
            t1 = t[0].split('.')
            last_time = "{}-{}-{}".format(t1[2], t1[1], t1[0]) + " " + t[1]

        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                article_url = 'https://www.sondakika.com' + article.select_one('li.nws >a.content').get('href')
                title = article.select_one('li > a.content > span').text
                abstract = article.select_one('li > p').text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'title': title, 'abstract':abstract})
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('#section > div > div.wrapper.detay-v3_3.haber_metni > p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = response.meta['abstract']
        item['images'] = [img.get('src') for img in soup.select('#section > div > div.RenderVideoOrImage > div >img')]
        time = soup.select_one('#section > div > div.hbptDate').text.split()
        nyr_time = time[0].split('.')[2] + '-' + time[0].split('.')[1] + '-' + time[0].split('.')[0]
        sfm_time = time[1] + ':00'
        pub_time = nyr_time + ' ' + sfm_time
        item['pub_time'] = pub_time
        yield item