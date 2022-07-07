from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

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


class sgcarmartSpider(BaseSpider):
    name = 'sgcarmart'
    website_id = 454
    language_id = 1866
    allowed_domains = ['sgcarmart.com']
    start_urls = ['https://www.sgcarmart.com/news/listing.php?CT=Articles']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True

        if self.time is not None:
            if soup.find(id='listing').select_one('.font_red') is not None:
                t = soup.find(id='listing').select_one('.font_red').text.strip().split()
                last_time = t[2]+'-'+month[t[1]]+'-'+t[0]+' 00:00:00'
            else:
                last_time = '2022-01-01 00:00:00'

        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.find(id='listing').find_all(style='width:560px')
            for article in articles:
                article_url = 'https://www.sgcarmart.com/news/' + article.select_one('a').get('href')
                title = article.select_one('a').text.strip()
                time = article.select_one('.font_red').text.strip().split()
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': None, 'category2': None,
                                    'title': title,
                                    'abstract': article.select_one('.font_12').text.strip(),
                                    'images': None,
                                    'time': time[2]+'-'+month[time[1]]+'-'+time[0]+' 00:00:00'})
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            if soup.select_one('a.pagebar') is not None:
                next_page = 'https://www.sgcarmart.com' + soup.select_one('a.pagebar').get('href')
                yield Request(url=next_page, callback=self.parse, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = soup.select_one('.label').text.strip().split('»')[-2] if soup.select_one('.label') else None
        item['category2'] = soup.select_one('.label').text.strip().split('»')[-1] if soup.select_one('.label') else None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = [soup.find(id='main_content').find(align='center').select_one('img').get('src')] if soup.find(id='main_content').find(align='center').select_one('img') else None
        item['abstract'] = response.meta['abstract']
        item['body'] = soup.find(id='main_content').text.strip()
        return item