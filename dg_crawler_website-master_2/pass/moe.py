# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
from copy import deepcopy

#   Author:叶雨婷
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


class MoeSpider(BaseSpider):
    name = 'moe'
    allowed_domains = ['moe.go.th']
    start_urls = ['https://www.moe.go.th/หมวด/ข่าว-ศธ-360-องศา']
    website_id = 1621
    language_id = 2208

    # 拿几个模块的的html文件的
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .dropdown-menu>a'):
            yield Request(url=i.get('href'), callback=self.get_page)

    # 按照日期边翻页边拿链接
    def get_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # t = soup.select('span', attrs={'class': '-date'})[-1].text.split(' ')这个不行，但也是css
        t = soup.select('span[class="-date"]')[-1].text.split(' ')
        last_time = str(int(t[2])-543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
        meta = {'pub_time_': last_time}
        for i in soup.select('div[class="-news-title -post-title"] a'):
            yield Request(url=i.get('href'), callback=self.parse_pages, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            yield Request(url=soup.select_one('a[rel="next"]').get('href'),
                          callback=self.get_page, meta=deepcopy(meta))
        else:
            self.logger.info("Time Stop")

    # 填表的
    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = soup.select_one(' .wrp-html').text.strip()
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] = soup.select_one(' .featured-media img').get('src')
        except:
            item['images'] = "None"
        try:
            item['body'] = soup.select_one('div[class="post-content clear"]').text.strip()
        except:
            item['body'] = "None"
        # 呃，外国网站有的好像只有标题
        item['category1'] = "新闻稿"
        item['abstract'] = " "
        # print(soup.select_one('div[class="category-and-date -single-category-and-date"] span').text)
        # print(soup.select_one(' .title-post-news span').text)
        item['category2'] = soup.select_one('span[class="-category"]').text
        # 原来是上面错了，这几个select都可以
        yield item




