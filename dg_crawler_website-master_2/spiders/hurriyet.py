# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

#author: 吴元栩
class HurriyetSpider(BaseSpider):
    name = 'hurriyet'
    website_id = 1818
    language_id = 2105
    type_list = ["dunya/","gundem/","cumartesi/","pazar/","lezzetli-hayat/","teknoloji/","haberleri/moda","haberleri/saglik"]
    start_urls = [f'https://www.hurriyet.com.tr/{type}?p={i}'for type in type_list for i in range(1,335)]

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        # 文章url列表
        list=soup.find_all(class_="category__list__item")
        for i in list:
            #文章页面url
            url1 = i.find(class_="category__list__item--cover").get("href")#content > section > div > div > div:nth-child(1) > a
            url = "https://www.hurriyet.com.tr"+url1
            # print(url)
            yield Request(url=url, callback=self.parse_page_content)

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # 文章标签类型
        tag = soup.find(class_="news-tags").text
        # 文章标题
        title = soup.find(class_="container").find("h1").text
        # 文章简介
        abstract = soup.find(class_="news-content__inf").find("h2").text
        # 发布时间
        pub_time_row= soup.find(class_="news-date").find("time").get("datetime")#.select_one("datetime")
        pub_time_list = pub_time_row.split("T")
        pub_time = pub_time_list[0]
        # 文章图片
        pic=[]
        try:
            pic1 = soup.find(class_="rhd-spot-img-cover").get("src")
        except:
            pic1 = None
        try:
            pic2 = soup.find(class_="news-fullwith-block").find("img").get("data-src")
        except:
            pic2 = None
        pic.append(pic1)
        pic.append(pic2)
        # 文章内容
        body=""
        bodylist = soup.find(class_="news-content").find_all("p")
        for i in bodylist:
            body = body+i.text+'\n'
        item = NewsItem()
        item['title'] = title
        item['category1'] = tag
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = pic
        yield item
