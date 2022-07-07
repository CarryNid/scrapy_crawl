from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
#author:李沐潼
from bs4 import BeautifulSoup as mutong
'''
新闻量少，没有写时间截止功能
'''
class mofaSpider(BaseSpider):
    name = 'mofa'
    website_id = 1335
    language_id = 1797
    start_urls = ['http://www.mofa.gov.mm']


    def parse(self, response):
        soup=mutong(response.text,'html.parser')
        category1=soup.select('.main-navigation-menu>.menu-item>a')[0].text
        category2_all = [i.text for i in soup.select('section>h1>b')]
        j=-1
        for i in soup.find_all(style='text-align:right'):
            url = 'http://www.mofa.gov.mm' + i.select('a')[0].get('href')[1:]
            j=j+1
            yield Request(url,meta={'category1':category1,'category2':category2_all[j]},callback=self.parse_page)

    def parse_page(self,response):
        soup = mutong(response.text,'html.parser')
        for news in soup.select('section>article>h2>a'):
            url=news.get('href')
            yield Request(url,meta=response.meta,callback=self.parse_item)
        try:
            next_page_url = soup.select('.post-pagination>.next')[0].get('href')
            yield Request(next_page_url,meta=response.meta,callback=self.parse_page)
        except:
            pass

    def parse_item(self,response):
        item = NewsItem()
        soup=mutong(response.text,'html.parser')
        new=''
        for i in soup.select('article>.entry>p'):
            try:
                new=new+i.text
            except:pass


        pic = [i.get('src') for i in soup.select('article>.entry>figure>img')]
        title=soup.select('article>h1')[0].text
        if pic!=[]:
            item['images']=pic
        else:
            item['images']=None
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body']=new
        item['abstract']=soup.select('article>.entry>p')[0].text
        item['title']=title
        item['pub_time'] = DateUtil.time_now_formate()
        yield item