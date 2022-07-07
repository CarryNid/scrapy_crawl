# encoding: utf-8
import json
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
#author:钟钧仰
class GmanetworkSpider(BaseSpider):
    name = 'gmanetwork'
    website_id = 1913
    language_id = 1880
    start_urls = ['https://www.gmanetwork.com/news/balitambayan/']

    def parse(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        menu = soup.select('#nav-main > div > a')
        first_url='https://data2.gmanews.tv/gno/widgets/grid_reverse_listing/story_btb'
        for i in menu:

            response.meta['category1']= i.text
            response.meta['id']=1
            yield Request(url=first_url+i.text.lower().replace('!','').replace(' ','')+'/1',callback=self.parse_page,meta=response.meta)

    def parse_page(self,response):
        menu=json.loads(response.text)
        news_list=menu['data']
        if len(menu['next_url'])!=0:#翻页
            response.meta['id']=response.meta['id']+1
            yield Request(url=menu['next_url'],callback=self.parse_page,meta=response.meta)
        else :
            self.logger.info("时间截至")
        for i in news_list:
            # print(i.get('publish_timestamp'),'https://www.gmanetwork.com/news/'+i.get('article_url'))
            if self.time and DateUtil.formate_time2time_stamp(i.get('publish_timestamp'))<int(self.time):
                continue
            response.meta['pub_time']=i.get('publish_timestamp')
            response.meta['abstract']=i.get('lead')
            response.meta['title']=i.get('title')
            response.meta['images']='https://www.gmanetwork.com/news/'+i.get('article_url')
            yield Request(url='https://www.gmanetwork.com/news/'+i.get('article_url'),callback=self.parse_item,meta=response.meta)


    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        all_p=soup.select('#stories > div:nth-child(1) > article p')
        p_list=[]
        for i in all_p:
            p_list.append(i.text)
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '/n'.join(p_list)
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        yield item
