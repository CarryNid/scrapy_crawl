# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
import json

#author: 吴元栩
class SabahSpider(BaseSpider):
    name = 'sabah'
    website_id = 1838
    language_id = 2105
    type_list = ["gundem","ekonomi","yasam","saglik","dunya","turizm"]
    start_urls = [f'https://www.sabah.com.tr/{type}'for type in type_list]
    # start_urls = ['https://www.sabah.com.tr/gundem']

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        url_list = json.loads(eval(str(soup).split("JSON.parse(")[1].split(");")[0]))
        for i in url_list:
            if str(i["Url"])[0:6]!="https":
                url = "https://www.sabah.com.tr"+i["Url"]
            else:
                url = i["Url"]
            yield Request(url=url, callback=self.parse_page_content)


    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text,'html.parser')

        try:
            # 发布时间
            pub_time_row = soup.find(class_="textInfo align-center").find("span").text
            pub_time_list = pub_time_row.split('.')
            pub_time_day = pub_time_list[0].split(':')[1].split(' ')[1]
            pub_time_year = pub_time_list[2].split('\n')[0].split(' ')[0]
            pub_time = f"{pub_time_year}-{pub_time_list[1]}-{pub_time_day}"
        except:
            return

        # 文章类型
        category_list = soup.find(class_="breadcrumb").find_all("span")
        category1 = ""
        category2 = ""
        t=int(1) #t是计数器，因为类型是有三部分构成，最后一部分是文章名称，所以只存取前两部分即可，用计数器做判断
        for i in category_list:
            if t==1:
                category1 = i.find("a").text
                t+=1
            elif t==2:
                category2 = i.find("a").text
                t+=1

        # 文章标题
        title = soup.find(class_="pageTitle").text

        # 文章内容
        body = ""
        body = soup.find(class_="newsDetailText").text
        body = body.strip()#去首尾空格

        # 文章简介
        try:
            abstract = soup.find(class_="spot selectionShareable").text
        except:
            abstract = body.split('\n')[0]#如果没有就用第一段代替

        # 图片
        img = []
        try:
            pic = soup.find(class_="newsImage").find("img").get("src")
        except:
            pic = None
        img.append(pic)

        item = NewsItem()
        item['title'] = title
        item['category1'] = category1
        item['category2'] = category2
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = img
        yield item




