from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class DeutschlandSpider(BaseSpider):  # author：田宇甲
    name = 'deutschland'
    website_id = 1779
    language_id = 1898
    start_urls = ['https://www.deutschland.de/de/news?tid=All&page=0']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .views-infinite-scroll-content-wrapper.clearfix .views-row article'):
            meta = {'title_': i.select_one(' .cover__inner .typoHm').text, 'category1_': 'News', 'abstract_': i.select_one(' .cover__inner .cover__text').text, 'images_': ['https://www.deutschland.de/'+i.picture.img['data-src']]}
            yield Request('https://www.deutschland.de/'+i.select_one(' .cover__image a')['href'], callback=self.check_check, meta=meta)
        yield Request(response.url.split('page=')[0]+'page='+str(int(response.url.split('page=')[1])+1))

    def check_check(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select_one(' .story__date').text.split('.')
        time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
            item = NewsItem()
            item['title'] = response.meta['title_']
            item['category1'] = response.meta['category1_']
            item['category2'] = None
            item['body'] = soup.select_one(' .story__content').text.strip().strip('\n')
            item['abstract'] = response.meta['abstract_']
            item['pub_time'] = time_
            item['images'] = response.meta['images_']
            yield item

