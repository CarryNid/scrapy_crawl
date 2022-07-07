from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

TURKISH_MONTH = {
    'Ocak': '01',
    'Şubat': '02',
    'Mart': '03',
    'Nisan': '04',
    'Mayıs': '05',
    'Haziran': '06',
    'Temmuz': '07',
    'Ağustos': '08',
    'Eylül': '09',
    'Ekim': '10',
    'Kasžm': '11',
    'Aralžk': '12'
}

# author : 李玲宝
class cinbilgisiSpiderSpider(BaseSpider):
    name = 'cinbilgisi'
    website_id = 1845
    language_id = 2227
    start_urls = ['https://www.cinbilgisi.com/cin-halk-cumhuriyeti/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#menu-menu1 a')
        for i in category1:
            yield scrapy.Request(i['href'], callback=self.parse_page, meta={'category1': i.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('#posts-container')
        flag = True
        if self.time is not None:
            t = block[-1].select_one('span.date.meta-item.tie-icon').text.split(' ')
            last_time = f'{t[2]}-{TURKISH_MONTH[t[1]]}-{t[0]}' + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for i in block:
                yield Request(i.select_one('.post-title>a')['href'], callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('span.last-page.first-last-pages > a') is None:
                self.logger.info("no more pages")
            else:
                yield Request(url=soup.select_one('span.last-page.first-last-pages > a')['href'], callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('.post-title.entry-title').text
        item['abstract'] = soup.select_one('.entry-content.entry.clearfix>p').text
        tt = soup.select_one('span.date.meta-item.tie-icon').text.split(' ')
        item['pub_time'] = f'{tt[2]}-{TURKISH_MONTH[tt[1]]}-{tt[0]}' + ' 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('.entry-content.entry.clearfix img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content.entry.clearfix'))
        return item
