# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

# check:why
# author: robot_2233
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


class dailynewsSpider(BaseSpider):  # 一个简单的静态爬虫，到底了就会报错然后停下来，分了article和news两种新闻都可以爬。
    name = 'dailynews'
    website_id = 238
    language_id = 2208
    start_urls = [f'https://www.dailynews.co.th/news/news_group/{i}' for i in ['ทั่วไทย-กทม', 'politics-news', 'บันเทิง', 'อาชญากรรม', 'เศรษฐกิจ-ยานยนต์', 'ไลฟ์สไตล์', 'กีฬา', 'การศึกษา-ไอที']]
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .elementor-widget-container article'):
            ssd = i.select_one(' .elementor-post-date').text.split()
            time_ = str(int(ssd[-1]) - 543) + '-' + Tai_MONTH[ssd[1]] + '-' + (ssd[0] if int(ssd[0]) >= 10 else '0' + ssd[0]) + ' 00:00:00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meat = {'title_': i.select_one(' .elementor-post__title').text.strip('\n'),
                        'time_': time_,
                        'category1_': response.url.split('news_group/')[1] if '/' not in response.url.split('news_group/')[1] else response.url.split('news_group/')[1].split('/')[0],
                        'images_': i.a.div.img['src']}
                yield Request(i.a['href'], callback=self.parse_item, meta=meat)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'page' not in response.url:
                yield Request(response.url + '/page/2', meta=meat)
            else:
                yield Request(response.url.replace('page/' + response.url.split('page/')[1], 'page/' + str(int(response.url.split('page/')[1].strip('/')) + 1)+'/'), meta=meat)

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .elementor-widget-container p')])
        item['abstract'] = soup.select_one(' .elementor-widget-container p').text
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item


