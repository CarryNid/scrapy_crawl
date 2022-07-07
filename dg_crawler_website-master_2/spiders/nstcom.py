from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date

# author : 林泽佳
class NstcomSpider(BaseSpider):
    name = 'nstcom'
    #allowed_domains = ['nst.com']
    website_id = 148
    language_id = 1866
    start_urls = ['https://www.nst.com.my/'] #https://www.nst.com.my/


    def parse(self, response):#初始页面，解析列表和其他数据
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#main > div > div.row')
        for category in categories:
            yield Request(url='https:' + category.get('href'), callback=self.parse_page,
                          meta={'category1': category.text})

    def parse_cate2(self, response):#点进不同分类的初始界面
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('#navbarToggler > div > ul > li'):
            ##navbarToggler > div > ul > li
            if i.get('href') == '//www.nst.com.my/':
                continue
            if i.get('href') == 'news':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3,
                              meta={'category1': response.meta['category1'], 'category2': i.text})
            if i.get('href') == 'business/home':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3,
                              meta={'category1': response.meta['category1'], 'category2': i.text})
            if i.get('href') == 'lifestyle':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3,
                              meta={'category1': response.meta['category1'], 'category2': i.text})
            if i.get('href') == 'sports':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3,
                              meta={'category1': response.meta['category1'], 'category2': i.text})
            if i.get('href') == 'world':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3,
                              meta={'category1': response.meta['category1'], 'category2': i.text})
            if i.get('href') == 'opinion':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3,
                              meta={'category1': response.meta['category1'], 'category2': i.text})

    def parse_cate3(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories1 = soup.select('#main > div')
        for category1 in categories1:
            yield Request(url='https:' + category1.get('href'), callback=self.parse_page,
                          meta={'category1': response.meta['category1'],'category2': response.meta['category2']})

    def parse_page(self, response):#点进文章里面的内容
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('#main > div > div.row > div.col > div:nth-child(1) > div')
        for article in articles:
            article_url = 'https://www.nst.com.my/'+ article.get('href')
            title = article.select_one('h1 > span').text#main > div > div.row > div.col > div:nth-child(1) > div > h1 > span
            tt = article.select_one('#div > div.d-block.d-lg-flex.mb-3 > div.article-meta.mb-2.mb-lg-0.d-flex.align-items-center > div').text.replace(',', ' ').split(' ')#div > div.d-block.d-lg-flex.mb-3 > div.article-meta.mb-2.mb-lg-0.d-flex.align-items-center > div
            pub_time = "{}-{}-{}".format(tt[3], date.ENGLISH_MONTH[tt[0]], tt[1]) + ' 00:00:00'
            yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'category2': response.meta['category2'], 'title': title, 'pub_time': pub_time})

    def parse_item(self, response):#存进item里面的数据
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('#main > div > div.row > div.col > div:nth-child(1) > div > div > div.article-content > div:nth-child(1) > div > div > figure > img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('#main > div > div.row > div.col > div:nth-child(1) > div > div > div.article-content > div.field.field-body > div') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item