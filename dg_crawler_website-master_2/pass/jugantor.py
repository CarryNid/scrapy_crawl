# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
import re
import time

##author : 吴元栩

#孟加拉语对照表
BENGAL_DATE ={
        #月份
        'জানুয়ারি': '01',
        'ফেব্রুয়ারি':'02',
        'মার্চ': '03',
        'এপ্রিল': '04',
        'মে': '05',
        'জুন': '06',
        'জুলাই': '07',
        'আগস্ট': '08',
        'সেপ্টেম্বর': '09',
        'অক্টোবর': '10',
        'নভেম্বর': '11',
        'ডিসেম্বর': '12',
        #数字
        '০': '0',
        '১': '1',
        '২': '2',
        '৩': '3',
        '৪': '4',
        '৫': '5',
        '৬': '6',
        '৭': '7',
        '৮': '8',
        '৯': '9'
}

class JugantorSpider(BaseSpider):
    name = 'jugantor'
    allowed_domains = ['jugantor.com']
    start_urls = [f"https://www.jugantor.com/all-news?page={i}" for i in range(1,51)]
    website_id = 1922
    language_id = 1799

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        i = soup.select('a')
        news_list_old = []
        for news_url in i:
            news_list_old.append(news_url.get('href'))
        news_list_old = news_list_old[124:164]
        news_list = sorted(set(news_list_old), key=news_list_old.index)
        for i in news_list:
            yield Request(url=i, callback=self.parse_page_content)

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')

        #文章标题
        page_title = soup.select_one('#news-title > h3').text
        print(page_title)

        #文章时间,按年月日
        page_time_raw = soup.select_one("#rpt-date > div.row.row-cols-2.pb-2 > div:nth-child(1) > div:nth-child(2) ").text
        page_time_deal = page_time_raw.split(',', 1)
        date = page_time_deal[0]
        datel = date.split(" ")
        day = datel[1]
        dayf = BENGAL_DATE[list(day)[0]]
        days = BENGAL_DATE[list(day)[1]]
        month = BENGAL_DATE[datel[2]]
        year = datel[3]
        year1 = BENGAL_DATE[list(year)[0]]
        year2 = BENGAL_DATE[list(year)[1]]
        year3 = BENGAL_DATE[list(year)[2]]
        year4 = BENGAL_DATE[list(year)[3]]
        pub_time = "{}{}{}{}-{}-{}{}".format(year1,year2,year3,year4,month,dayf,days)

        #文章内容
        page_paragraph_above = soup.select('#myText >p')#//*[@id="myText"]/p[1]/text()
        page_paragraph = ""
        for i in page_paragraph_above :
            page_paragraph+=i.text+'\n'

        #图片网址
        page_picture_above = soup.find_all(class_="dtl-news-img")
        img_href = re.findall(r'href="(.*?)"',str(page_picture_above))

        item = NewsItem()
        item['category1'] = 'news'
        item['title'] = page_title
        item['pub_time'] = pub_time
        item['body'] = page_paragraph
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = img_href
        # time.sleep(5)
        return item
