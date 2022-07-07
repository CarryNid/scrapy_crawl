# encoding: utf-8
from bs4 import BeautifulSoup
from datetime import datetime
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
#author:钟钧仰
class BangkatriunnewsSpider(BaseSpider):
    name = 'bangkatribunnews'
    website_id = 39
    language_id = 1952
    start_urls = ['https://aceh.tribunnews.com/']

    def parse(self,response):
        # soup=BeautifulSoup(response.text,'lxml')
        first_url = 'https://bangka.tribunnews.com/index-news?date='
        seconde_url = '&page=1'
        month1 = {1, 3, 5, 7, 8, 10, 12}
        month2 = {4, 6, 9, 11}
        fin_date='2010-09-20'
        t = datetime.today()
        now_year = t.year
        now_month = t.month
        now_day = t.day
        now_date = str(now_year) + '-' + str(now_month).rjust(2, '0') + '-' + str(now_day).rjust(2, '0')
        #最早的新闻时间：2010-9-20
        for year in range(now_year, 2009, -1):
            for month in range(12, 0, -1):
                for day in range(31, 0, -1):
                    date = str(year) + '-' + str(month).rjust(2, '0') + '-' + str(day).rjust(2, '0')
                    #判断日期合法：
                    leap = False  # 判断是否为闰年
                    legal = False  # 判断是否合法
                    # 判断月份是否为闰年
                    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
                        leap = True
                    if month in month1:
                        if 1 <= day <= 31:
                            legal= True
                    elif month in month2:
                        if 1 <= day <= 30:
                            legal= True
                    elif month == 2:
                        if not leap and 1 <= day <= 28:
                            legal= True
                        elif leap and 1 <= day <= 29:
                            legal= True

                    if now_date >= (date) and legal and date>=fin_date:
                        if self.time is None or (self.time and DateUtil.formate_time2time_stamp(date+' 00:00:00') > int(self.time)):
                            news_page_url = first_url + date + seconde_url
                            response.meta['time']=date+' 00:00:00'
                            yield Request(url=news_page_url,callback=self.parse_page,meta=response.meta)
                        else :
                            self.logger.info("时间截至")
                            break
    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        menu = soup.select('body > div.main > div.content > div.fl.w677 > div > div:nth-child(2) > div.pt10.pb10 > ul > li')
        for i in menu:
            response.meta['title']=i.select_one('h3 > a').text
            yield Request(url=i.select_one('h3 > a').get('href'),callback=self.parse_item,meta=response.meta)
        #判断是否翻页
        tmp = (soup.select('#paginga > div.paging > a'))
        for i in tmp:
            if (i.text == 'Next'):
                next_url = i.get('href')
                yield Request(url=next_url,callback=self.parse_page,meta=response.meta)


    def parse_item(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem()
        try:
            item['category1'] = soup.select_one('#va > ul > li:nth-child(2) > a > span ').text
            if((soup.select_one('#va > ul > li:nth-child(2) > a > span ').text !='Video')):
                item['category2'] = soup.select_one('#va > ul > li:nth-child(3) > a > span ').text
                all_p = soup.select_one('#article_con > div.side-article.txt-article.multi-fontsize ')
                p_list = []
                p_list.append(all_p.text)
                for i in all_p.select('p'):
                    p_list.append(i.text)
                item['title'] = response.meta['title']
                item['body'] = '/n'.join(p_list)
                item['abstract'] = all_p.text
                item['pub_time'] = response.meta['time']
                item['images'] = []
                yield item
        except:
            pass
