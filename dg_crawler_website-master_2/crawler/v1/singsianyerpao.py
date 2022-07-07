from crawler.spiders import BaseSpider
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

month = {
        '一月': '01',
        '二月': '02',
        '三月': '03',
        '四月': '04',
        '五月': '05',
        '六月': '06',
        '七月': '07',
        '八月': '08',
        '九月': '09',
        '十月': '10',
        '十一月': '11',
        '十二月': '12'
}

day = {
        '1': '01',
        '2': '02',
        '3': '03',
        '4': '04',
        '5': '05',
        '6': '06',
        '7': '07',
        '8': '08',
        '9': '09',
}


# author 武洪艳
class SingsianyerpaoSpider(BaseSpider):
    name = 'singsianyerpao'
    # allowed_domains = ['www.singsianyerpao.com/']
    start_urls = ['http://www.singsianyerpao.com/']  # http://www.singsianyerpao.com/
    website_id = 1598  # 网站的id(必填)
    language_id = 1813  # 语言
    is_http = 1
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'root',
    #     'password': 'why520',
    #     'db': 'dg_crawler'
    # }

    # 这是类初始化函数，用来传时间戳参数


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-main-menu-ch > li > a')[1:9]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        t = soup.select('.post-date')[-6].text.replace(',', ' ').split(' ')
        if len(t[1]) == 1:
            last_time = "{}-{}-{} 00:00:00".format(t[3], month[t[0]], day[t[1]])
        else:
            last_time = "{}-{}-{} 00:00:00".format(t[3], month[t[0]], t[1])
        if self.time is None or Util.format_time3(last_time) >= int(self.time):
            articles = soup.select('div.col-title > h3 > a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('div.pagination.clearfix > div > a.nextpostslink') is not None:
                next_page = soup.select_one('div.pagination.clearfix > div > a.nextpostslink').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#content > div.page-header > h1').text
        tt = soup.select_one('#content > div.page-header > div > span').text.replace(',', ' ').split(' ')
        if len(tt[1]) == 1:
            item['pub_time'] = "{}-{}-{} 00:00:00".format(tt[3], month[tt[0]], day[tt[1]])
        else:
            item['pub_time'] = "{}-{}-{} 00:00:00".format(tt[3], month[tt[0]], tt[1])
        image_list = []
        imgs = soup.select('#content > div.content-detail img')
        if imgs:
            for img in imgs:
                image_list.append(img.get('src'))
            item['images'] = image_list
        p_list = []
        if soup.select('#content > div.content-detail p'):
            all_p = soup.select('#content > div.content-detail p')
            for paragraph in all_p:
                if paragraph.text.strip() != ' ' and paragraph.text.strip() != '\n':
                    p_list.append(paragraph.text.strip())
            body = '\n'.join(p_list)
        item['body'] = body
        if p_list[0] != '':
            item['abstract'] = p_list[0]
        else:
            if p_list[1] != '':
                item['abstract'] = p_list[1]
            else:
                if p_list[2] != '':
                    item['abstract'] = p_list[2]
                else:
                    if p_list[3] != '':
                        item['abstract'] = p_list[3]
        return item

