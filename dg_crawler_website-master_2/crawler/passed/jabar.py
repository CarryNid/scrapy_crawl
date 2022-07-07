from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import json


# Author:田宇甲
class JabarSpider(BaseSpider):
    name = 'jabar'#动态
    website_id = 36
    language_id = 1952
    start_urls = ["https://jabar.tribunnews.com/ajax/latest?start=0",
                  "https://jabar.tribunnews.com/ajax/latest_section?&section=22&section_name=kesehatan&start=0",
                  "https://jabar.tribunnews.com/ajax/latest_section?&section=17&section_name=travel&start=0",
                  "https://tribunjabartravel.tribunnews.com/ajax/latest_section?&section=1&start=0"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in json.loads(soup.text)['posts']:
            if self.time is None or DateUtil.formate_time2time_stamp(i['date'].split('+')[0].replace('T', ' ')) + 3200 >= int(self.time):
                meta = {'pub_time_': i['date'].split('+')[0].replace('T', ' '), 'title_': i['title'], 'abstract_': i['introtext'], 'images_': i['thumb'], 'category1_': 'news'}
                yield Request(i['url'], callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(i['date'].split('+')[0].replace('T', ' ')) + 3200 >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            tyj = str(response.url).split('start=')[0]+'start='+str(int(str(response.url).split('start=')[-1])+20)
            yield Request(tyj)

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = '\n'.join(i.text for i in soup.select(' .side-article.txt-article.multi-fontsize'))
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        return item