# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup


#   Author:叶雨婷
Tai_MONTH = {
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
        'ธันวาคม': '12'}

class EnergySpider(BaseSpider):
    name = 'energy'
    start_urls = ['https://energy.go.th/2015/category/minister-news-th/']
    website_id = 1614
    language_id = 2208

    # 由于分类一次后每篇文章没有显示时间，所以这个parse没有时间判断
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('h2[class="entry-title"] a'):
            yield Request(url=i.get('href'), callback=self.parse_time)
        try:
            yield Request(url=soup.select_one(' .next.page-numbers').get('href'))
            # 翻页
        except AttributeError:
            pass

    # 每一篇文章都进行一次parse_time，顺便item
    def parse_time(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        t = soup.select_one('time').text.split(',')[1].split(' ')
        last_time = str(t[3]) + "-" + Tai_MONTH[t[2]] + "-" + str(t[1]) + " 00:00:00"
        item = NewsItem()
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            item['title'] = soup.select_one('header[class="entry-header"]').text
            item['pub_time'] = last_time
            item['images'] = soup.select_one('img').get('src')
            try:
                item['body'] = soup.select_one(' .entry-content p').text
            except AttributeError:
                item['body'] = 'None'
            item['category1'] = "หน้าแรก"
            item['abstract'] = " "
            item['category2'] = "ข่าวสารรัฐมนตรี"
            yield item
