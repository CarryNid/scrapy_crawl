# encoding: utf-8
from time import sleep

from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from utils.util_old import Util
from scrapy.http.request import Request
import json
# author : 钟钧仰
class denrspider(BaseSpider):
    name = 'denr'
    website_id = 1257
    language_id = 1866
    start_urls = ['https://www.denr.gov.ph/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        menu = soup.select('#auxiliary > div > div > nav > section > ul.left > li')[2].select('ul > li')
        urls = 'https://newsalertapi.denr.gov.ph/fetchPublic_NewsArticle.php'
        yield Request(url=urls, callback=self.parse_news_page, meta=response.meta)
        for i in range(0, 4):
            page_url = 'https://www.denr.gov.ph' + menu[i].select_one('a').get('href')
            response.meta['category1'] = (menu[i].select_one('a').text)
            yield Request(url=page_url,callback=self.parse_item,meta=response.meta)


    def parse_item(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        menu = soup.select('#content > div > div.blog > div')
        item=NewsItem()
        flag=True
        time = menu[1].select_one('div > div > dl > dd > time').get('datetime').split('T')
        last_time = time[0] + ' ' + time[1].split('+')[0]
        if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(last_time):
            for i in range(1, len(menu)-1):
                item['title'] = menu[i].select_one('div > div > div.page-header >h2').text.strip()
                item['category1']=response.meta['category1']
                item['category2']=None
                p_list = []
                all_p = menu[i].select('div > div  p')
                if len(all_p) <= 1 :
                    all_p = menu[i].select('div > div > div')
                    for l in range(0, len(all_p)):
                        if (all_p[l].text.strip() != 'Print'):
                            p_list.append(all_p[l].text.strip())
                else:
                    for l in all_p:
                        if l.text != " ":
                            p_list.append(l.text.strip())
                item['body']='\n'.join(p_list)
                t=0
                while t<len(p_list)-1 and len(p_list[t]) <5 : t+=1
                item['abstract']=p_list[t]
                try:
                    item['images'] = 'https://www.denr.gov.ph/'+menu[i].select_one('article > div > div > div.icons > div > ul > li > a').get('href')
                except:
                    pass
                time = menu[i].select_one('div > div > dl > dd > time').get('datetime').split('T')
                item['pub_time'] = time[0] + ' ' + time[1].split('+')[0]
                yield item
        else:

            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page ='https://www.denr.gov.ph'+menu[6].select_one('ul > li.pagination-next > a').get('href')
                yield Request(url=next_page, callback=self.parse_item, meta=response.meta)
            except:
                pass
    # 子网站的爬取
    def parse_news_page(self,response):
        data=json.loads(response.text)
        for i in data:
            t = i.get('articleDate').replace(',', '').split(' ')
            response.meta['pub_time'] = t[2] + '-' + str(Util.month[t[0]]).rjust(2, '0') + '-' + t[1] + " 00:00:00"
            response.meta['category2'] =i.get('articleCategory')
            last_time_=response.meta['pub_time']
            news_url='https://newsalertapi.denr.gov.ph/fetchPublic_NewsArticle_Row.php'
            data1= {'id':(i.get('articleGUID'))}
            # print(int(i),response.meta['pub_time'] ,i.get('articleTitle'))
            if self.time is None or int(self.time) < DateUtil.formate_time2time_stamp(last_time_):
                yield scrapy.FormRequest(url=news_url,callback=self.parse_item2,meta=response.meta, method='POST', formdata=data1)
            else:
                self.logger.info("时间截至")
                break

    def parse_item2(self, response):
        items=NewsItem()
        # soup=BeautifulSoup(response.text,'lxml')
        data = json.loads(response.text)
        items['title']=data[0].get('articleTitle')
        items['category1']=data[0].get('articleTypeName')
        items['category2']=data[0].get('articleCategoryName')
        items['images']=data[0].get('articleImage')
        items['pub_time']=response.meta['pub_time']
        items['body']=data[0].get('articleBody')
        items['abstract']=data[0].get('articleKeywords')
        yield items


