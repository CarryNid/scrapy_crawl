from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from scrapy.http.request import Request

# author : 武洪艳
class MmkunmingcnSpider(BaseSpider):
    name = 'mmkunmingcn'
    website_id = 2066
    language_id = 2065
    # allowed_domains = ['mm.kunming.cn/']
    start_urls = ['https://mm.kunming.cn/']  # https://mm.kunming.cn/
    # 大多页面404，新闻量较少

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('div.visible-desktop.pc-nav > div > ul > li a')[1:]
        for category in categories:
            yield Request(url='https://mm.kunming.cn' + category.get('href'), callback=self.parse_page, meta={'category1': category.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('div.span8 > div.page-list > ul > li > div > div > h3 > a')
        for article in articles:
            if article.get('href').split(':')[0]=='https':
                article_url = article.get('href')
            else:
                article_url = 'https://mm.kunming.cn' + article.get('href')
            title = article.text
            yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'title': title, })
        if soup.select_one('div.span8 > div.page-list > div > ul > li.active + li a') == None:
            self.logger.info("no more pages")
        else:
            next_page = response.url.split('index')[0] + soup.select_one('div.span8 > div.page-list > div > ul > li.active + li a').get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        if response.url == 'https://mm.kunming.cn':
            self.logger.info("no articles")
        else:
            item['category1'] = response.meta['category1']
            item['title'] = soup.select_one('.page-content h1').text
            item['pub_time'] = soup.select_one('.page-content span.time').text + ':00'
            item['images'] = ['https://mm.kunming.cn'+img.get('src') for img in soup.select('.post-content img')]
            item['body'] = '\n'.join(
                [paragraph.text.strip() for paragraph in soup.select('.post-content') if
                 paragraph.text != '' and paragraph.text != ' '])
            item['abstract'] = item['body'].split('\n')[0]
            return item
