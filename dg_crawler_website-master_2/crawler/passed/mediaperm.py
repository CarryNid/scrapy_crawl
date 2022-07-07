# encoding: utf-8
import re
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
#author: robot_2233
ENGLISH_MONTH = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'}


class MediapermSpiderSpider(BaseSpider):
    name = 'mediaperm'
    website_id = 221
    language_id = 2029
    start_urls = ['http://mediapermata.com.bn/']
    # is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.find_all(class_=re.compile("menu-item menu-item-type-taxonomy menu-item-object-category td-menu-item td-mega-menu menu-item")):
            yield Request(url=i.a.get('href'),  callback=self.holy_shit)

    def holy_shit(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .td-block-row .td_module_1.td_module_wrap.td-animation-stack'):
            ssd=i.select_one(' .td-post-date').text.split()
            time_=ssd[-1]+'-'+ENGLISH_MONTH[ssd[0]]+'-'+ssd[1].split(',')[0]+' 00:00:00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meta = {'pub_time_': time_}
                meta['CA']=str(response.url).split('/category/')[1]
                yield Request(url=i.h3.a.get('href'), callback=self.parse_item,meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
            yield Request(url=soup.select(' .page-nav.td-pb-padding-side a')[-1].get('href'),  callback=self.holy_shit)


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select_one(' .entry-title').text
        item['category1'] = response.meta['CA']
        item['category2'] = None
        item['body'] = soup.select_one(' .td-post-content.tagdiv-type').text
        item['abstract'] = soup.select_one(' .td-post-content.tagdiv-type p').text
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] = [i.img.get('src') for i in soup.select_one(' .td-post-content.tagdiv-type').find_all(class_='wp-caption aligncenter')]
        except:
            item['images'] = []
        yield item
