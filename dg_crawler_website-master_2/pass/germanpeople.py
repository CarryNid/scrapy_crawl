from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class germanpeopleSpider(BaseSpider):  # author：田宇甲
    name = 'germanpeople'
    website_id = 1791
    language_id = 1898
    start_urls = [f'http://german.people.com.cn/{i}/index1.html' for i in ['209052','209053','209054','414966','414967']]
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .fl ul li'):
            ssd = i.text.split('[')[1].strip(']').split(' ')[0].split('/')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' ' + i.text.split('[')[1].strip(']').split(' ')[1] +':00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meta = {'pub_time_': time_, 'title_': i.text.split('[')[0]}
                yield Request('http://german.people.com.cn'+i.a['href'], callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.split('index')[0]+'index'+str(int(response.url.split('index')[1].split('.')[0])+1)+'.html')

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = 'Index'
        item['category2'] = None
        item['body'] = soup.select_one(' .txt_con.clearfix').text.strip().strip('\n')
        item['abstract'] = soup.select_one(' .txt_con.clearfix p').text.strip().strip('\n') if len(soup.select_one(' .txt_con.clearfix p').text.strip().strip('\n')) >10 else soup.select_one(' .txt_con.clearfix').text.strip().strip('\n').split('\n')[0]
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = None  # 确实没有图片，非常离谱
        yield item
