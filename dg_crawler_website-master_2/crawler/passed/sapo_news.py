# encoding: utf-8
from bs4 import BeautifulSoup
import json
import utils.date_util
from common.date import ENGLISH_MONTH
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# Author:陈卓玮
class sapo_news(BaseSpider):
    name = 'sapo_news'
    website_id = 2068
    language_id = 2122
    start_urls = ['https://www.sapo.pt']

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        columns = []
        for i in soup.select('#header > nav.\[.ink-navigation.\].primary-menu > div > ul > li > a'):
            if i.get('href'):
                columns.append({'category1': i.text, 'url': self.start_urls[0]+i.get('href')})
        for i in soup.select("#header > nav.\[.ink-navigation._hide-tiny._hide-small._hide-medium.\].secondary-menu > div > ul > li > a")[1]:
            try:
                if 'https' in i.get('href'):
                    columns.append({'category1': i.text, 'url': i.get('href')})
                else:
                    columns.append({'category1': i.text, 'url': self.start_urls[0]+i.get('href')})
            except:
                pass

        for i in columns:
            yield Request(url = i['url'],meta={'columns':i},callback=self.ctgy1_parser)

    def ctgy1_parser(self,response):
        #因为网站结构问题 时间截止功能对少部分文章不起作用
        meta = response.meta
        soup = BeautifulSoup(response.text, 'lxml')
        page_list = []
        page_list = set(page_list)

        if len(soup.select('section > ul > li'))>2:
            for i in soup.select('section > ul > li'):
                for k in i.select('span'):
                    if k.get('data-timestamp') != None:
                        t = int(k.get('data-timestamp'))/1000
                if 'https' in i.select_one('a').get('href'):
                    if self.time == None or int(t) >= self.time or t==None:
                        # print(utils.date_util.DateUtil.time_stamp2formate_time(t))
                        page_list.add(i.select_one('a').get('href'))

        if len(soup.select('.content > ul > li'))>2:
            for i in soup.select('.content > ul > li'):
                for k in i.select('span'):
                    if k.get('data-timestamp') != None:
                        t = int(k.get('data-timestamp'))/1000
                if 'https' in i.select_one('a').get('href'):
                    if self.time == None or int(t) >= self.time or t==None:
                        # print(utils.date_util.DateUtil.time_stamp2formate_time(t))
                        page_list.add(i.select_one('a').get('href'))

        if len(soup.select('body > div.\[.ink-grid.vertical-padding.\].main.page-category.page-category--opiniao > div > div > ul > li'))>2:
            for i in soup.select('body > div.\[.ink-grid.vertical-padding.\].main.page-category.page-category--opiniao > div > div > ul > li'):
                for k in i.select('span'):
                    if k.get('data-timestamp') != None:
                        t = int(k.get('data-timestamp'))/1000
                if i.select_one('a').get('href') and 'https' in i.select_one('a').get('href'):
                    if self.time == None or int(t) >= self.time or t==None:
                        # print(utils.date_util.DateUtil.time_stamp2formate_time(t))
                        page_list.add(i.get('href'))


        try:
            next_page = soup.select_one('body > div.\[.ink-grid.vertical-padding.\].main.page-category.page-category--opiniao > div > div > nav > ul > li.next > a').get('href')
            yield Request(url = "https://www.sapo.pt/opiniao"+next_page,callback=self.ctgy1_parser,meta=meta)
        except:
            pass

        for i in page_list:
            if "https://24.sapo.pt/jornais" not in i and 'sapo.pt' in i and "videos" not in i:
                if 'https' not in i:
                    url = "https://www.publico.pt"+i
                else:
                    url = i
                yield Request(url = url,meta = meta,callback=self.essay_parser)

    def essay_parser(self,response):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'lxml')
        #获取标题
        try:
            title = soup.select_one('#article-title').text.strip()
        except:
            title = soup.select_one('h1').text.strip()
            if title=='':
                title = soup.select_one('.title').text.strip()



        global time
        #获取pubtime
        try:#尝试抓包json
            for i in soup.select('script'):
                if i.get('type') == 'application/ld+json':
                    text = i.text.strip('\n').encode('utf8').decode('unicode_escape')
                    json_data = json.loads(text, strict=False)

            try:
                time = (json_data['dateCreated'])
            except:
                for i in json_data['@graph']:
                    if (i['@type'] == 'WebPage'):
                        time = (i['dateCreated'])
        except:
            try:#尝试直接获取时间
                for i in soup.select('head > meta'):
                    if i.get('property') == 'og:updated_time' or i.get('property')=='article:published_time':
                        time = (i.get('content'))
            except:
                time = (soup.select_one('time').get('datetime'))

        #格式化时间
        try:
            time = utils.date_util.DateUtil.time_stamp2formate_time(time)
        except:
            time = time.replace('T', ' ').replace('Z', ' ').split('+')[0]

        #获取content
        article_content = ''
        for i in soup.select('p'):
            if i.text.replace('\n', '') != '':
                article_content += i.text.replace('\n', '') + '\n'
        #获取img
        img = []
        img = set(img)
        for i in soup.select('img'):
            if (i.get('src') != None and 'svg' not in i.get('src')):
                img.add(i.get('src'))
        img = list(img)
        abstract = article_content.split('\n')[0]


        item = NewsItem()
        item['title'] = title
        item['category1'] = meta['columns']['category1']
        item['category2'] = ''
        item['body'] = article_content
        item['abstract'] = abstract
        item['pub_time'] = time
        item['images'] = img
        return item

