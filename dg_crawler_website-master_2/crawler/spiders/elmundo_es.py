from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


class elmundo_esSpider(BaseSpider):
    name = 'elmundo_es'
    website_id = 1276
    language_id = 2181
    allowed_domains = ['elmundo.es']
    start_urls = ['http://www.elmundo.es']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        menu = soup.find(class_='ue-c-main-navigation__list ue-c-main-navigation__list--first-level').select('li.ue-c-main-navigation__list-item a')
        for item in menu:
            if item.get('href') is not None:
                category_url = item.get('href')
                meta = {'category1': item.text}
                yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('div.ue-l-cover-grid article')
        for article in articles:
            article_url = article.select_one('a').get('href')
            yield Request(url=article_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('.ue-l-article__header-content').text.strip() if soup.select_one('.ue-l-article__header-content') else None
        item['pub_time'] = soup.select_one('.ue-c-article__publishdate time').get('datetime').replace('T',' ').replace('Z','') if soup.select_one('.ue-c-article__publishdate time') else '2022-01-01 00:00:00'
        item['images'] = [soup.select_one('picture img').get('src')] if soup.select_one('picture img') else None
        item['abstract'] = soup.select_one('.ue-c-article__standfirst').text.strip() if soup.select_one('.ue-c-article__standfirst') else None
        p_list = []
        if soup.find(class_='ue-l-article__body ue-c-article__body'):
            all_p = soup.find(class_='ue-l-article__body ue-c-article__body').select('p')
            for paragraph in all_p:
                try:
                    p_list.append(paragraph.text.strip())
                except:
                    continue
            body = '\n'.join(p_list)
            item['body'] = body
        return item