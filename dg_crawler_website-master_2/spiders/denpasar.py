# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.items import *
from crawler.spiders import BaseSpider
from scrapy.http.request import Request
from utils.date_util import DateUtil
from copy import deepcopy
# author:hejiale

class DenpasarSpider(BaseSpider):
    name = 'denpasar'
    website_id = 71
    language_id = 1809
    start_urls = ['http://denpasar.china-consulate.gov.cn/chn/']
    e = ''
    is_http = 1

    def parse(self, response):
        list_pages = ["xwdt","zyxw","fyrth"]
        for i in list_pages:
            self.e = i
            meta = {'e' : i}
            yield Request(url=self.start_urls[0] + i, callback=self.next_page, meta=meta)

    def next_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if self.time is not None:
            t = soup.select('.middle ul li ')[0].text.split('(')[1].strip(')').split('/')
            tt = "{}-{}-{}".format(t[0], t[1], t[2]) + ' 00:00:00'
        if self.time == None or DateUtil.formate_time2time_stamp(tt) >= self.time:
            for k in range(0, 14):
                if k == 0:
                    n_url = 'http://denpasar.china-consulate.gov.cn/chn/' + response.meta['e'] + '/index.htm'
                else:
                    n_url = 'http://denpasar.china-consulate.gov.cn/chn/' + response.meta['e'] + '/index_' + str(k) + '.htm'
                yield Request(url=n_url, callback=self.sub_parse, meta=response.meta)

    def sub_parse(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        l = soup.select('.middle ul li ')
        if self.time is not None:
            t =l[0].text.split('(')[1].strip(')').split('/')
            tt = "{}-{}-{}".format(t[0], t[1], t[2]) + ' 00:00:00'
        if self.time == None or DateUtil.formate_time2time_stamp(tt) >= self.time:
            for i in l:
                ur = i.select_one('a').get('href').strip('.').strip('/')
                url3 = 'http://denpasar.china-consulate.gov.cn/chn/' + response.meta['e'] + '/' + ur
                yield Request(url=url3,callback =self.get_item)

    def get_item(self,response):
        items = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        items['category1'] = 'news'
        try:
            items['title'] = soup.select_one('#News_Body_Title').text
        except:
            items['title'] = ''
        try:
            items['pub_time'] = soup.select_one('#News_Body_Time').text
        except:
            items['pub_time'] = ''
        News_Content = ''
        text = soup.select('#News_Body_Txt_A ')

        for t in text:
            News_Content = News_Content + t.text.strip() + '\n'
        items['body'] = News_Content
        img_url = []
        try:
            img = soup.select('.News_Body_Text img')
            for i in img:
                img_url.append(str(response.url.split('/t')[0] + i.get('src').strip('.')))
            items['images'] = list(img_url)
        except:
            img = None
        items['abstract'] = items['body'].split('\n')[0]
        yield items