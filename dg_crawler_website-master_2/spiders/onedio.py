# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

#author: 吴元栩
class OnedioSpider(BaseSpider):
    name = 'onedio'
    website_id = 1868
    language_id = 2105
    type_list = ["gundem","ekonomi","magazin","finans","seyahat","gaming","yemek","yasam","saglik","teknoloji","nasil-yapilir","egitim","genel-kultur"]
    # type_list = ["gundem"]#"spor","goygoy"
    start_urls = [f'https://onedio.com/{type}/{i}'for type in type_list for i in range(1,100)]

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        url_list = soup.find_all(class_="o-linkbox__overlay hover:text-link-primary")
        for i in url_list:
            url_row = i.get("href")
            url = "https://onedio.com"+url_row
            yield Request(url=url, callback=self.parse_page_content)

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        # 文章标题
        title = soup.find(class_="text-24 text-black-500 sm:text-26 font-bold leading-snug").text
        # 文章类型
        tag = ""
        tag_row = soup.find(class_="mt-1 categories text-md text-primary-200 flex")
        tag_list = tag_row.find_all("a")
        for i in tag_list:
            tag = tag + i.text
            tag += ">"
        # 文章时间
        pub_time_row= soup.find(class_="flex items-center leading-16 text-sm text-primary-300 space-x-3 px-4").text
        pub_time_list = pub_time_row.split('.')
        pub_time_day_list = pub_time_list[0].split('\n')
        pub_time_year_list = pub_time_list[2].split(" ")
        pub_time = pub_time_year_list[0]+"-"+pub_time_list[1]+"-"+pub_time_day_list[1]#+"-"+pub_time_year_list[2]
        pub_time = pub_time.replace(" ",'')

        # 文章简介
        abstract = ""
        try:
            abstract_list = soup.find(class_="entry entry--text text").find_all("p")
            for i in abstract_list:
                abstract = abstract+i.text
        except:
            abstract = None

        # 文章图片
        pic = []
        try:
            pic_list = soup.find_all(class_="image relative")
        except:
            pic_list = None
        for i in pic_list:
            pic1=i.find("img").get("src")
            pic.append(pic1)

        # 文章内容
        # 有些是问卷，有些是新闻
        body_all = soup.find(class_="article sm:pt-7.5 relative px-2.5 sm:pl-14 sm:pr-5")
        body=""
        body_list=[]
        try:
            try:
                body_list += body_all.find_all(class_="entry entry--image image")
            except:
                body_list += body_all.find(class_="entry entry--image image")
        except:
            try:
                try:
                    body_list += body_all.find_all(class_="entry entry--video video")
                except:
                    body_list += body_all.find(class_="entry entry--video video")
            except:
                body_all = soup.find(class_="article sm:pt-7.5 relative px-2.5 sm:pl-14 sm:pr-5 quiz")
                body_list += body_all.find_all(class_="entry entry--question question")
        for i in body_list:
            try:
                body_row = i.find("p").text
                body += body_row
            except:
                try:
                    body_row = i.find("h2").text
                except:
                    body_row=""
                body+=body_row

        item = NewsItem()
        item['title'] = title
        item['category1'] = tag
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = pic
        yield item