# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
import requests


#author : 吴元栩
class OcaibSpider(BaseSpider):

    name = 'ocaib'
    allowed_domains = ['www.ocaib.org']
    start_urls = [f"https://www.ocaib.org/nr.jsp?m31pageno={i}" for i in range(1,4)]#全站的文章集合列表
    website_id = 1917  # 网站的id(必填)
    language_id = 1813  # 语言

    def parse(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, "html.parser")
        i = soup.find_all(class_="newsCalendar")  # class="newsTitle"  class="J_newsResultLine line nline fk-newsLineHeight"
        for news_url in i:
            href = news_url.find("a")
            # print(href)
            if href !=-1 :
                if href != None :
                    url ="http://www.ocaib.org/" + href.get("href")
                    pub_time = href.string
                    item['pub_time'] = pub_time
                    yield Request(url=url,meta={"item": item},callback=self.parse_item)

    def parse_item(self, response):
        item = response.meta["item"]
        soup = BeautifulSoup(response.text, 'html.parser')
        content_all = soup.find(class_="richContent")
        i = content_all.find_all('p')
        content_ac = ""
        imgsrc = []
        for x in i:
            content = x.find_all('span')
            for k in content:
                if str(k.string) != "None":
                    content_ac = content_ac + str(k.string)
            img = x.img
            if img != None:
                imgsrc.append(img['src'])
        title = soup.find(class_="title").text
        # title = title.string
        item['title'] = title
        item['category1'] = soup.find(class_="newsGroupTag").text
        item["images"] = imgsrc
        item["body"] = content_ac
        item['abstract'] = item['body'].split('\n')[0]
        yield item
