from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from bs4 import BeautifulSoup
from scrapy.http.request import Request

# author: 蔡卓妍
class IdMofcomSpider(BaseSpider):
    name = 'id_mofcom'
    website_id = 129
    language_id = 2266
    start_urls = ['http://id.mofcom.gov.cn/']
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.select(".navCon.f-fl li")[1:-1]:
            if "http" in i.select_one('a').get('href'):
                new_url = i.select_one('a').get('href')
            else:
                new_url = 'http://id.mofcom.gov.cn/' + i.select_one('a').get('href')
            if i.select_one('a').text != 'China Policy':
                meta = {'category1':i.select_one('a').text}
                yield Request(url=new_url, meta=meta, callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            flag = True
            last_time =soup.select('.row.wms-con > div > section.listCon.f-mt30 > section > section > ul > li > span')[-1].text
            if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
                articles = soup.select(".listCon.f-mt30 > section > section > ul > li ")
                for i in articles:
                    if i.select_one('a') != None:
                        response.meta['title'] = i.select_one('a').text
                        response.meta['pub_time'] = i.select_one('span').text
                        article = 'http://id.mofcom.gov.cn'+i.select_one('a').get('href')
                        yield Request(url=article,meta=response.meta,callback=self.parse_items)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag: # 翻页
                p = response.url.split('/')[-1][1:]
                if p == '':
                    p = 1
                    next_page = response.url + f"?{str(int(p) + 1)}"
                else:
                    next_page = response.url.replace(str(p), f"{str(int(p) + 1)}")
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info("no more pages")

    def parse_items(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        if soup.select('#zoom') != None:
            item['body'] = "\n".join(i.text.strip() for i in soup.select('#zoom'))
        if soup.select_one('.art-title') is not None:
            item['abstract'] = soup.select_one('.art-title').text
        item['pub_time'] = response.meta['pub_time']
        item['images'] = []
        yield item