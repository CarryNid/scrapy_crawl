from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import json


# Author:黄锦荣
# check: 凌敏 一些问题已修改，常报403，该网站无category 可pass
class kishoraloSpider(BaseSpider):
    name = 'kishoralo'#动态
    website_id = 1898
    language_id = 1779
    start_urls = ["https://www.kishoralo.com/feapi/push-engage-notifications?limit=10&offset=1"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in json.loads(soup.text)['notifications']:
            meta = {'pub_time_': i['sent_time'], 'title_': i['notification_title'], 'abstract_': i['notification_message'], 'images_': i['notification_image']}
            yield Request(i['notification_url'], callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(i['sent_time']) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('offset='+response.url.split('offset=')[1], 'offset='+str(int(response.url.split('offset=')[1])+1)), callback=self.parse)

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = None
        item['category2'] = None
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div/div/div/div/p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
