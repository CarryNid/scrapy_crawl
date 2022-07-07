# encoding: utf-8
from bs4 import BeautifulSoup
from utils.util_old import Util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class DemoSpiderSpider(BaseSpider):
    name = 'dpwh'
    website_id = 1258
    language_id = 1866
    start_urls = ['https://www.dpwh.gov.ph/dpwh/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        menu=soup.select('#aux-nav > section > ul > li')
        for i in range(1, 3):
            news_page_url = 'https://www.dpwh.gov.ph' + menu[i].select_one('a').get('href')
            response.meta['category1'] = menu[i].select_one('a').text
            yield Request(url=news_page_url,callback=self.parse_page,meta=response.meta)

    def parse_page(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        news_page=soup.select('#content > div > div > div.view-content > div > ul > li')
        flag=True
        if response.meta['category1'] == 'News':
            t = news_page[0].select('div')[3].select('span')[1].text.replace(',', '').split()
            last_time = t[2] + '-' + str(Util.month[t[0]]).rjust(2,'0') + '-' + t[1].rjust(2,'0') + " 00:00:00"
        else:
            t = news_page[0].select('div')[3].select('span')[1].text.split(' ')
            last_time=t[4] + '-' + str(Util.month[t[3]]).rjust(2,'0') + '-' + t[1].replace('th', '').replace('st', '').replace('nd', '').rjust(2,'0')+ " 00:00:00"
        if self.time is None or int(self.time)<DateUtil.formate_time2time_stamp(last_time):
            for i in news_page:
                if response.meta['category1']=='News':
                    t = i.select('div')[3].select('span')[1].text.replace(',', '').split()
                    response.meta['time'] = t[2] + '-' + str(Util.month[t[0]]).rjust(2,'0') + '-' + t[1] .rjust(2,'0')+ " 00:00:00"
                else :
                    t = i.select('div')[3].select('span')[1].text.split(' ')
                    response.meta['time']= t[4] + '-' + str(Util.month[t[3]]).rjust(2,'0') + '-' + t[1].replace('th', '').replace('st', '').replace('nd', '').rjust(2,'0') + " 00:00:00"
                news_url='https://www.dpwh.gov.ph' + i.select('div')[2].select_one('a').get('href')
                response.meta['title']=i.select_one('div > span > a').text
                try:
                    response.meta['abstract']= i.select_one(' div > div > p').text
                except:
                    response.meta['abstract'] = None
                yield Request(url=news_url,callback=self.parse_item,meta=response.meta)
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page_url='https://www.dpwh.gov.ph' +soup.select_one('#content > div > div > div.item-list > ul > li.pager-next > a').get('href')
                yield Request(url=next_page_url, callback=self.parse_page, meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['time']
        if response.meta['category1'] == 'News':
            try:
                images = soup.select_one('#content > div > article > div.field.field-name-field-featured-image.field-type-image.field-label-hidden > div > div > img').get('src')
            except:
                images=None
        else :
            try:
                images = soup.select_one('#content > div > article > div.field.field-name-field-announcement-image.field-type-image.field-label-hidden > div > div > a').get('href')
            except:
                images=None
        item['images'] = images
        all_p = soup.select('#content > div > article > div > div > div > p')
        p_list = []
        for t in all_p:
            try:
                p_list.append(t.text)
            except:
                continue
        item['body'] = '\n'.join(p_list)
        yield item
