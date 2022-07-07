from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date

# author:武洪艳
class GnlmcommmSpider(BaseSpider):
    name = 'gnlmcommm'
    website_id = 1469
    language_id = 1866
    # allowed_domains = ['www.gnlm.com.mm/']
    start_urls = ['https://www.gnlm.com.mm/']  # https://www.gnlm.com.mm/
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-menu-1 > li')[1:9]
        for category in categories:
            category1 = category.select_one('li > a').text
            for i in category.select('li > ul > li > a'):
                yield Request(url=i.get('href'), callback=self.parse_page, meta={'category1': category1, 'category2': i.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.col-md-8 > div.row.archives-page > article')
        if soup.select('div.col-md-8 > div.row.archives-page > article')==[]:
            self.logger.info("no articles")
        else:
            if self.time is not None:
                t = articles[-1].select_one('.post-content .post-date').text.replace(',', ' ').split(' ')
                last_time = "{}-{}-{}".format(t[4], date.ENGLISH_MONTH[t[1]], t[2]) + ' 00:00:00'
            if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
                for article in articles:
                    tt = article.select_one('.post-content .post-date').text.replace(',', ' ').split(' ')
                    pub_time = "{}-{}-{}".format(tt[4], date.ENGLISH_MONTH[tt[1]], tt[2]) + ' 00:00:00'
                    article_url = article.select_one('.post-content .post-title a').get('href')
                    title = article.select_one('.post-content .post-title a').text
                    yield Request(url=article_url, callback=self.parse_item,
                                  meta={'category1': response.meta['category1'], 'category2': response.meta['category2'], 'title': title, 'pub_time': pub_time})
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                if soup.select_one('div.col-md-8 > div.navigation > ol > li a.next') == None:
                    self.logger.info("no more pages")
                else:
                    next_page = soup.select_one('div.col-md-8 > div.navigation > ol > li a.next').get('href')
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.col-md-8 > article img') if (img.get('src').split(':')[0]!='data')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('.col-md-8 > article') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
