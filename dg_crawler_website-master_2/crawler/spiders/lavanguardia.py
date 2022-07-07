from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


class lavanguardiaSpider(BaseSpider):
    name = 'lavanguardia'
    website_id = 1279
    language_id = 2181
    allowed_domains = ['lavanguardia.com']
    start_urls = ['https://www.lavanguardia.com/']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        menu = soup.find(class_='hamburger-menu container').find_all(itemprop='name')
        del(menu[-7:])
        no_url = ['https://www.lavanguardia.com/temas','https://www.lavanguardia.com/comer','https://www.lavanguardia.com/comprar','https://www.lavanguardia.com/motor','https://www.lavanguardia.com/de-moda','https://www.lavanguardia.com/ocio/viajes','https://www.lavanguardia.com/magazine','https://www.lavanguardia.com/tecnologia','https://www.lavanguardia.com/comprar/comparativas/','https://www.lavanguardia.com/historiayvida','https://www.lavanguardia.com/horoscopo','https://www.lavanguardia.com/blogs']
        for item in menu:
            if item.select_one('a').get('href') is not None and item.select_one('a').get('href').find('www') is not -1 and item.select_one('a').get('href') not in no_url:
                category_url = item.select_one('a').get('href')
                meta = {'category1': item.text.strip()}
                yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select_one('.section-list').select('.result-news') if soup.select_one('.section-list') else None
        for article in articles:
            if article.select_one('a') is not None:
                article_url = 'https://www.lavanguardia.com' + article.select_one('a').get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)

        if soup.select_one('li.next a') is not None:
            next_page = 'https://www.lavanguardia.com' + soup.select_one('li.next a').get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('.title').text.strip() if soup.select_one('.title') else None
        item['pub_time'] = time = soup.select_one('.date-time .modified').get('datetime').replace('T',' ').replace('+01:00','') if soup.select_one('.date-time .modified') else '2022-01-01 00:00:00'
        item['images'] = [soup.select_one('picture img').get('src')] if soup.select_one('picture img') else None
        p_list = []
        if soup.select_one('.article-modules'):
            all_p=soup.select_one('.article-modules').select('p')
            for paragraph in all_p:
                try:
                    p_list.append(paragraph.text.strip())
                except:
                    continue
            body = '\n'.join(p_list)
            item['abstract'] = p_list[0]
            item['body'] = body
        return item