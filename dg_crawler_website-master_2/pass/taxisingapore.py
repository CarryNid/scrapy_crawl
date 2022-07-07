

from scrapy import Request
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import requests
from bs4 import BeautifulSoup as mutong

e_month_sim={
        'Jan':'01',
        'Feb':'02',
        'Mar':'03',
        'Apr':'04',
        'May':'05',
        'Jun':'06',
        'Jul':'07',
        'Aug':'08',
        'Sept':'09',
        'Sep':'09',
        'Oct':'10',
        'Nov':'11',
        'Dec':'12'
}

class taxisingaporeSpider(BaseSpider):#爬出来的文章均没有图片
    # #网站两年未更新，新闻量少。用时间截止均403或520 不用时间截止很正常
    name = 'taxisingapore'
    proxy='02'
    website_id = 453
    language_id = 1866
    custom_settings = {'DOWNLOAD_TIMEOUT': 60}
    start_urls = ['https://www.taxisingapore.com/taxi-stories/']


#aurhor：李沐潼

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}
        meta['category1']='Taxi Stories'
        url = soup.select('h2>a')
        for u in url:
            yield Request(u.get('href'),meta=meta,callback=self.parse_items)
        next_url=soup.select('.next')
        if next_url==[]:
            pass
        else:
            nu=next_url[0].get('href')
            yield Request(nu,meta=meta,callback=self.parse)

    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        t_list=soup.select('.date')[0].text.split(' ')
        if '' in t_list:
            t_list.remove('')
        ti ='{}-{}-{} 00:00:00'.format(t_list[2], e_month_sim[t_list[1]], t_list[0])
        if self.time is None or DateUtil.formate_time2time_stamp(ti) >= int(self.time):

            item = NewsItem()
            body = ''.join([i.text for i in soup.select('p')])
            item['title'] = soup.select('.mainbar>h1')[0].text
            item['abstract'] = soup.select('p')[0].text
            item['category1'] = response.meta['category1']
            item['category2'] = None
            item['body']=body
            item['pub_time'] = ti
            item['images'] =None
            # print(item)
            yield item

