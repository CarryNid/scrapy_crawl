# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

class DenrSpiderSpider(BaseSpider):
    name = 'denr'
    website_id = 1257
    language_id = 1866
    start_urls = ['https://www.denr.gov.ph/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        menu = soup.select('#auxiliary > div > div > nav > section > ul.left > li')[2].select('ul > li')
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
            for i in range(1, 6):
                item['title'] = menu[i].select_one('div > div > div.page-header >h2').text.strip()
                item['category1']=response.meta['category1']
                item['category2']=None
                p_list = []
                all_p = menu[i].select('div > div > p')
                if len(all_p) == 0 or all_p[0].text== '\xa0':
                    all_p = menu[i].select('div > div > div')
                    for l in range(4, len(all_p)):
                        p_list.append(all_p[l].text)
                else:
                    for l in all_p:
                        p_list.append(l.text)
                item['body']='\n'.join(p_list)
                item['abstract']=p_list[0]
                if response.meta['category1']!='FEATURES':
                    try:
                        image = 'https://www.denr.gov.ph/' + menu[i].select('div >div >div')[3].select_one('img').get('src')
                    except:
                        continue
                else :
                    try:
                        image = 'https://www.denr.gov.ph/' + menu[i].select('div >div >p')[1].select_one('img').get('src')
                    except:
                        try:
                            image = 'https://www.denr.gov.ph/' + menu[i].select('div >div >p')[2].select_one('img').get('src')
                        except:
                            continue
                item['images']=image
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