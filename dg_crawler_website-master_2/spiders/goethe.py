from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

German_month = {
    'Januar': '01',
    'Februar': '02',
    'März': '03',
    'April': '04',
    'Mai': '05',
    'Juni': '06',
    'Juli': '07',
    'August': '08',
    'September': '09',
    'Oktober': '10',
    'November': '11',
    'Dezember': '12'
}

class GoetheSpider(BaseSpider):  # author：田宇甲
    name = 'goethe'
    website_id = 1773
    language_id = 1898
    start_urls = ['https://www.goethe.de/de/uun/prs/p21.html']  # 无需翻页， 很少的新闻， 爱来自瓷器

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .span12.nurText .row'):
            meta = {'title_': i.h3.text.strip(), 'category1_': 'News', 'abstract_': i.p.text}
            yield Request('https://www.goethe.de/de/'+i.select_one(' a:nth-child(2)')['href'].split('de/')[1], callback=self.check_check, meta=meta)

    def check_check(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select_one(' .erste').text.strip().split(' ')
        time_ = ssd[-1] + '-' + German_month[ssd[0]] + '-01 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
            item = NewsItem()
            item['title'] = response.meta['title_']
            item['category1'] = response.meta['category1_']
            item['category2'] = None
            item['body'] = soup.select_one(' .span12.nurText').text.strip().strip('\n')
            item['abstract'] = response.meta['abstract_']
            item['pub_time'] = time_
            item['images'] = []  # 新闻无图片
            yield item

