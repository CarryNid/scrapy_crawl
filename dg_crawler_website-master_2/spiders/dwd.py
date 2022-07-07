from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class DwdSpider(BaseSpider):  # author：田宇甲
    name = 'dwd'
    website_id = 1784
    language_id = 1898
    start_urls = ['https://www.dwd.de/DE/service/archiv/archiv_node.html']  # 天气新闻网站

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .textualData.links tr')[1:]:
            ssd = i.text.strip().split(' ')[0].strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                if 'pollenflug' not in i.a['href'] and 'bodenfeuchte' not in i.a['href'] and 'klimakarten' not in i.a['href']:
                    if 'klima_' not in i.a['href'] and 'bodenfrost' not in i.a['href'] and 'beobachtungen' not in i.a['href']:# 有些不是新闻
                        meta = {'pub_time_': time_, 'title_': i.text.strip().split(' ', 1)[1].strip(),  'category1_': 'Interessantes'}
                        yield Request('https://www.dwd.de/'+i.a['href'], callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request('https://www.dwd.de/'+soup.select(' .pagination-index li')[-1].a['href'])

    def parse_item(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .article-full').text.strip().strip('\n')
        item['abstract'] = soup.select_one(' .body-text p').text.strip().strip('\n')
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = []  # 这个网站没有图片，离谱
        yield item
