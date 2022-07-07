from crawler.spiders import BaseSpider
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

days = {
        'ชั่วโมงก่อน': 'hours ago',
}

THAIMONTH = {
        'มกราคม': '01',
        'กุมภาพันธ์': '02',
        'มีนาคม': '03',
        'เมษายน': '04',
        'พฤษภาคม': '05',
        'มิถุนายน': '06',
        'กรกฎาคม': '07',
        'สิงหาคม': '08',
        'กันยายน': '09',
        'ตุลาคม': '10',
        'พฤศจิกายน': '11',
        'ธันวาคม': '12',
        'ม.ค.': '01',
        'ก.พ.': '02',
        'มี.ค.': '03',
        'เม.ย.': '04',
        'พ.ค.': '05',
        'มิ.ย.': '06',
        'ก.ค.': '07',
        'ส.ค.': '08',
        'ก.ย.': '09',
        'ต.ค.': '10',
        'พ.ย.': '11',
        'ธ.ค.': '12',
    }

# author 武洪艳
class KhaosodcothhomeSpider(BaseSpider):
    name = 'khaosodcothhome'
    # allowed_domains = ['www.khaosod.co.th/home']
    start_urls = ['https://www.khaosod.co.th/home']  # https://www.khaosod.co.th/home
    website_id = 1569  # 网站的id(必填)
    language_id = 2208  # 语言
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
        for i in soup.select('div.ud-mm__menus > ul > li')[1:11]:
            category_url = i.select_one('a').get('href')
            meta = {'category1': i.select_one('a').text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if self.time is not None:
            t = soup.select('.col-md-4 .udblock__metaleft span')[-1].text.split(' ')
            if len(t) == 3:
                last_time = str(int(t[2]) - 543) + '-' + Util.THAIMONTH[t[1]] + '-' + t[0] + ' 00:00:00'
            else:
                last_time = Util.format_time2(t[0] + ' ' + days[t[1]])
        if self.time is None or Util.format_time3(last_time) >= int(self.time):
            articles = soup.select('div.udblock__text-display.udblock__text-display--top_down.udblock__text-display--bordered > div > h3 > a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select('div.udpg > ul > li > a')[-1].get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('.udsg__main-title').text.strip()
        tt = soup.select_one('div.container.ud-padding .udsg__meta-left span.udsg__meta').text.split(' ') # 无参数，表示空格分隔。
        item['pub_time'] = str(int(tt[2]) - 543) + '-' + THAIMONTH[tt[1]] + '-' + tt[0] + ' 00:00:00'
        item['images'] = [img.get('data-src') for img in soup.select('div.container.ud-padding > div.udsg__featured-image-wrap img')]
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('.udsg__content') if paragraph.text!='' and paragraph.text!=' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item