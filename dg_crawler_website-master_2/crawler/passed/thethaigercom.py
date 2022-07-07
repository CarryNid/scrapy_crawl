from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author : 武洪艳
class ThethaigercomSpider(BaseSpider):
    name = 'thethaigercom'
    website_id = 1593
    language_id = 1866
    # allowed_domains = ['thethaiger.com/news']
    start_urls = ['https://thethaiger.com/news/']  # https://thethaiger.com/news
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-header-en-2022 > li:nth-child(1) > ul > li > a')
        for category in categories:
            category_url = category.get('href')
            if category_url == 'https://thethaiger.com/news/national':
                for i in soup.select('#menu-header-en-2022 > li:nth-child(1) > ul > li > ul > li > a'):
                    yield Request(url=i.get('href'), callback=self.parse_page, meta={'category1': category.text, 'category2': i.text})
            else:
                yield Request(url=category_url, callback=self.parse_page, meta={'category1': category.text,'category2': None})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.mvp-main-blog-in > div > ul > li')
        if self.time is not None:
            last_time = DateUtil.format_time_English(soup.select('span.mvp-cd-date.left.relative')[-1].text)
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                pub_time = DateUtil.format_time_English(article.select_one('span.mvp-cd-date.left.relative').text)
                article_url = article.select_one('a').get('href')
                title = article.select_one('div.mvp-blog-story-in > div > h2').text
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': response.meta['category1'], 'category2': response.meta['category2'], 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('div.mvp-inf-more-wrap.left.relative > div > div.pagination span.current + a') == None:
                self.logger.info("no more pages")
            else:
                next_page = soup.select_one('div.mvp-inf-more-wrap.left.relative > div > div.pagination span.current + a').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('#mvp-post-feat-img > img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('#mvp-post-content p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item

