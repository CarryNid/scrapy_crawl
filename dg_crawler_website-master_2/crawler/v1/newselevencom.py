from crawler.spiders import BaseSpider
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

month = {
        'JANUARY': '01',
        'January': '01',
        'FEBRUARY': '02',
        'February': '02',
        'MARCH': '03',
        'March': '03',
        'APRIL': '04',
        'April': '04',
        'MAY': '05',
        'May': '05',
        'JUNE': '06',
        'June': '06',
        'JULY': '07',
        'July': '07',
        'AUGUST': '08',
        'August': '08',
        'SEPTEMBER': '09',
        'September': '09',
        'OCTOBER': '10',
        'October': '10',
        'NOVEMBER': '11',
        'November': '11',
        'DECEMBER': '12',
        'December': '12'
}

day = {
        '1': '01',
        '2': '02',
        '3': '03',
        '4': '04',
        '5': '05',
        '6': '06',
        '7': '07',
        '8': '08',
        '9': '09',
}


# author 武洪艳
class NewselevencomSpider(BaseSpider):
    name = 'newselevencom'
    # allowed_domains = ['news-eleven.com/']
    start_urls = ['https://news-eleven.com/']  # https://news-eleven.com/
    website_id = 1468  # 网站的id(必填)
    language_id = 2065  # 语言
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'root',
    #     'password': 'why520',
    #     'db': 'dg_crawler'
    # }

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#block-system-main-menu > ul > li > a')[:10]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('.view-content .frontpage-title > a')
        for article in articles:
            article_url = article.get('href')
            yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        try:
            next_page = soup.select('.pager li a')[-2].get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('div.news-detail-title').text
        tt = soup.select_one('span.date-display-single').text.split(' ')
        if len(tt[0]) == 1:
            item['pub_time'] = "{}-{}-{} 00:00:00".format(tt[2], month[tt[1]], day[tt[0]])
        else:
            item['pub_time'] = "{}-{}-{} 00:00:00".format(tt[2], month[tt[1]], tt[0])
        image_list = []
        imgs = soup.select('div.news-detail-news-image-wrapper > div > img')
        if imgs:
            for img in imgs:
                image_list.append(img.get('src'))
            item['images'] = image_list
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.field-item.even') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item