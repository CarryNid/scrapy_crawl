from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date

# author : 武洪艳
class WowcordilleracomSpider(BaseSpider):
    name = 'wowcordilleracom'
    website_id = 1173
    language_id = 1866
    start_urls = ['https://www.wowcordillera.com/']  # https://www.wowcordillera.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#wrap2 > div:nth-child(5) > div > ul > li a')[1:6]
        del categories[3]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.blog-posts.hfeed .date-outer')
        if soup.select('div.blog-posts.hfeed .date-outer')==[]:
            self.logger.info("no articles")
        else:
            if self.time is not None:
                t = articles[-1].select_one('h2.date-header').text.replace(',', ' ').split(' ')
                last_time = "{}-{}-{}".format(t[5], date.ENGLISH_MONTH[t[2]], t[3]) + ' 00:00:00'
            if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
                for article in articles:
                    tt = article.select_one('h2.date-header').text.replace(',', ' ').split(' ')
                    pub_time = "{}-{}-{}".format(tt[5], date.ENGLISH_MONTH[tt[2]], tt[3]) + ' 00:00:00'
                    article_url = article.select_one('h3.post-title.entry-title a').get('href')
                    title = article.select_one('h3.post-title.entry-title a').text
                    yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'title': title, 'pub_time': pub_time})
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                if soup.select_one('#Blog1_blog-pager-older-link').get('href') == None:
                    self.logger.info("no more pages")
                else:
                    next_page = soup.select_one('#Blog1_blog-pager-older-link').get('href')
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.post-body.entry-content img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('.post-body.entry-content') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
