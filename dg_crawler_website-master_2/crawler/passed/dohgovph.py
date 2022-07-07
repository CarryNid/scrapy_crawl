# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.util_old import Util
from utils.date_util import DateUtil
from scrapy.http.request import Request
# author : 钟钧仰
class dohgovphSpider(BaseSpider):
    name = 'dohgovph'
    website_id = 1256
    language_id = 1866
    start_urls = ['https://doh.gov.ph/press-releases']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        div_obj=soup.select('#content > div > div > div.view-content > div.views-row')
        flag=True
        if self.time is None:
            for i in div_obj:
                news_url = "https://doh.gov.ph/" + i.select_one('a').get('href')
                t = i.select_one('div.views-field.views-field-created-1').text.replace(',', '').split()
                pub_time = t[2] + '-' + str(Util.month[t[0]]) + '-' + t[1] + " 00:00:00"
                response.meta['time']=pub_time
                response.meta['title']=i.select_one('a').text
                yield Request(url=news_url,callback=self.parse_item,meta=response.meta)
        else :
            t=div_obj[len(div_obj)-1].select_one('div.views-field.views-field-created-1').text.replace(',', '').split()
            last_time = t[2] + '-' + str(Util.month[t[0]]) + '-' + t[1] + " 00:00:00"
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                for i in div_obj:
                    news_url = "https://doh.gov.ph/" + i.select_one('a').get('href')
                    t = i.select_one('div.views-field.views-field-created-1').text.replace(',', '').split()
                    pub_time = t[2] + '-' + str(Util.month[t[0]]) + '-' + t[1] + " 00:00:00"
                    response.meta['time'] = pub_time
                    response.meta['title'] = i.select_one('a').text
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
            else :
                self.logger.info("时间截至")
                flag=False
        if flag:
            try:
                next_page="https://doh.gov.ph"+soup.select_one('#content > div > div > div.item-list > ul > li.pager-next > a').get('href')
                yield Request(url=next_page,callback=self.parse,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item=NewsItem()
        item['title']=response.meta['title']
        if soup.select_one('#content > div > article > div > div > div > p') is not None:
            item['category1']=soup.select_one('#content > div > article > div > div > div > p').text.split('|')[0]
        else:
            item['category1'] = 'news'
        item['category2']=None
        item['pub_time']=response.meta['time']
        item['images']=None
        try:
            item['body'] = '\n'.join(
                [paragraph.text.strip() for paragraph in soup.select('#content > div > article') if
                 paragraph.text != '' and paragraph.text != ' '])
        except:
            pass
        # all_p = soup.select('#content > div > article')
        # p_list = []
        # for i in range(1, len(all_p)):
        #     try:
        #         p_list.append(all_p[i].text)
        #     except:
        #         continue
        # item['body']='\n'.join(p_list)
        item['abstract'] = item['body'].split('\n')[0]
        yield item
