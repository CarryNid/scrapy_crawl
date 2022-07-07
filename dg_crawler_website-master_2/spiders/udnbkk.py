from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class ubnbkkSpider(BaseSpider):  # author：田宇甲 用时40分钟
    name = 'ubnbkk'
    website_id = 227
    language_id = 2266
    start_urls = ['http://www.udnbkk.com/portal.php?mod=list&catid=152&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=46&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=50&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=51&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=61&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=48&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=49&page=1',
                  'http://www.udnbkk.com/portal.php?mod=list&catid=91&page=1']
    proxy = '02'
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .fornews_bb .bb_div'):
            ssd = i.select_one(' .bb_div dl dd p').extract()
            dss = ssd.text.split('-')
            if int(dss[1]) < 10:
                dss[1] = '0' + dss[1]
            if int(dss[2].split(' ')[0]) < 10:
                dss[2] = '0' + dss[2]
            time_ = '-'.join(dss) + ':00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                meta = {'pub_time_': time_, 'title_': i.select_one(' .bb_divt').text, 'abstract_': i.select_one(' .bb_div dl dd').text, 'images_': 'http://www.udnbkk.com/'+i.dl.dt.a.img['src'] if i.dl.dt is not None else None, 'category1_': 'News'}
                yield Request(i.div.a['href'], callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('page='+response.url.split('page=')[1], 'page='+str(int(response.url.split('page=')[1])+1)))

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = '\n'.join([i.text for i in soup.find_all(style="margin-bottom: 0cm")])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
