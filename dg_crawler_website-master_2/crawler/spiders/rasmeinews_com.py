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


class rasmeinews_comSpider(BaseSpider):
    name = 'rasmeinews_com'
    website_id = 1873
    language_id = 999
    allowed_domains = ['rasmeinews.com']
    start_urls = ['https://www.rasmeinews.com/']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        menu = soup.find(class_='nav navbar-nav').select('li')[1].select('li')
        for i in menu:
            url = i.select_one('a').get('href')
            yield Request(url=url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True

        if self.time is not None:
            t = soup.select_one('.mg-blog-date').text.replace(',', '').split()
            last_time = t[2]+'-'+month[t[0]]+'-'+t[1]+' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.find(class_='mg-posts-sec-inner').select('article')
            for article in articles:
                article_url = article.select_one('.title a').get('href')
                title = article.select_one('.title a').text
                time_split = article.select_one('.mg-blog-date').text.replace(',', '').split()
                time = time_split[2]+'-'+month[time_split[0]]+'-'+time_split[1]+' 00:00:00'
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': None, 'category2': None,
                                    'title': title,
                                    'abstract': article.select_one('.mg-content').text.strip(),
                                    'images': None,
                                    'time': time})
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            if soup.find(class_='next page-numbers') is not None:
                next_page = soup.find(class_='next page-numbers').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = None
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = [response.meta['images']]
        item['abstract'] = response.meta['abstract']
        p_list = []
        if soup.find(class_='small single'):
            all_p = soup.find(class_='small single').select('p')
            for paragraph in all_p:
                try:
                    p_list.append(paragraph.text.strip())
                except:
                    continue
            body = '\n'.join(p_list)
            item['body'] = body
        return item