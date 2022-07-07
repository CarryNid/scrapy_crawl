from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
from utils.date_util import DateUtil


# author : 沈振兴

class KampucheathmeySpider(BaseSpider):
    name = 'kampucheathmey'
    allowed_domains = ['kampucheathmey.com']
    website_id = 1878
    language_id = 1982
    start_urls = ['https://www.kampucheathmey.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('#menu-main-menu-1 > li > a')[:-2]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text, 'page': '1', 'url': category_url}
            yield Request(url=category_url, meta=meta, callback=self.parse_page)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        d_date = {'០': '0', '១': '1', '២': '2', '៣': '3', '៤': '4', '៥': '5', '៦': '6', '៧': '7',
                  '៨': '8', '៩': '9', 'ម៉ោង': 'hour', 'ថ្ងៃ': 'day', 'ខែ': 'month', 'ឆ្នាំ': 'year', 'មុន': 'ago',
                  'សប្តាហ៍': 'week'}
        all_essays = soup.select('#mvp-main-body-wrap > div > div > div > div > div > div > ul > li a')
        if self.time is not None:
            t_ori = soup.select('ul > li span.mvp-cd-date')[-1].text.split()
            days = t_ori[0]
            s = 0
            for k in range(len(days)):
                s += int(d_date[days[k]]) * pow(10, len(days) - 1 - k)
            t = str(s) + ' ' + d_date[t_ori[1]] + ' ' + d_date[t_ori[2]]
            last_time = DateUtil.format_time_English(t)
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.select('#mvp-main-body-wrap > div > div > div > div > div > div > ul > li a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, meta=response.meta, callback=self.parse_item)
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            curr_page = int(response.meta['page']) + 1
            nextPage = response.meta['url'] + 'page/{}/'.format(curr_page)
            response.meta['page'] = str(curr_page)
            yield Request(url=nextPage, meta=response.meta, callback=self.parse_page)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        essay_time = soup.select_one('div.mvp-author-info-date.left.relative > meta').get('content')
        essay_time = essay_time[:-3] + ':00'
        response.meta['title'] = soup.select_one('header > h1').text
        response.meta['pub_time'] = essay_time
        images = [i.get('src') for i in soup.select('div > figure img')]
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('#mvp-content-main p') if
                                  paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        item['pub_time'] = response.meta['pub_time']
        item['images'] = images
        yield item
