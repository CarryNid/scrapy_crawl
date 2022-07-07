from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import re

month = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }


class pmo_gov_sgSpider(BaseSpider):
    name = 'pmo_gov_sg'
    website_id = 456
    language_id = 1866
    allowed_domains = ['pmo.gov.sg']
    start_urls = ['https://www.pmo.gov.sg/Newsroom']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True

        if self.time is not None:
            if soup.find(id='listing').select_one('.font_red') is not None:
                t = re.search('\d\d \w\w\w \d\d\d\d', soup.select_one('.results-container').select_one('.meta-data').text.strip()).group().split()
                last_time = t[2]+'-'+month[t[1]]+'-'+t[0]+' 00:00:00'
            else:
                last_time = '2022-01-01 00:00:00'

        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.select_one('.results-container').select('.field-content')
            for article in articles:
                article_url = 'https://www.pmo.gov.sg' + article.find(class_='snippet-content half-width').select_one('h2 a').get('href')
                title = article.find(class_='snippet-content half-width').select_one('h2').text.strip()
                time = re.search('\d\d \w\w\w \d\d\d\d', article.select_one('.meta-data').text.strip()).group().split()
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': article.select_one('.meta-data span').text.strip(), 'category2': None,
                                    'title': title,
                                    'abstract': None,
                                    'images': None,
                                    'time': time[2]+'-'+month[time[1]]+'-'+time[0]+' 00:00:00'})
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            if soup.select_one('.next a') is not None:
                next_page = 'https://www.pmo.gov.sg/Newsroom' + soup.select_one('.next a').get('href')
                yield Request(url=next_page, callback=self.parse, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = ['https://www.pmo.gov.sg/' + soup.select_one('.hero-banner').select_one('img').get('src')] if soup.select_one('.hero-banner').select_one('img') else None
        item['abstract'] = soup.select_one('.summary').text.strip() if soup.select_one('.summary') else None
        p_list = []
        if soup.find(class_='col-sm-12 col-md-6 col-md-offset-3'):
            all_p = soup.find(class_='col-sm-12 col-md-6 col-md-offset-3').select('p')
            for paragraph in all_p:
                try:
                    p_list.append(paragraph.text.strip())
                except:
                    continue
            body = '\n'.join(p_list)
            item['body'] = body
        return item