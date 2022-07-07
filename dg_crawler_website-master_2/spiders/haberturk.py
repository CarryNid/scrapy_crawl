# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

#author: 吴元栩
class HaberturkSpider(BaseSpider):
    name = 'haberturk'
    website_id = 1819
    language_id = 2105
    type_list = ["saglik",  "yasam", "dunya",  "magazin","one-cikanlar","ekonomi", "spor","gundem"]
    start_urls = [f'https://www.haberturk.com/son-dakika-haberleri/{type}/infiniteLoad?page={i}'for type in type_list for i in range(1,39)]
    # start_urls = [f'https://www.haberturk.com/son-dakika-haberleri/one-cikanlar/infiniteLoad?page={i}'for i in (13,317)]
    proxy = '02' # 如果爬虫需要代理，加上这一行成员变量，否则别加。

    # 文章总量不多

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        if len(str(soup).strip())==0:
            return
        else:
            url_list = soup.find_all(class_="box-background box-news")
            for i in url_list:
                if str(i.find("a").get("href"))[0:6] != "https":
                    url = "https://www.haberturk.com/"+ i.find("a").get("href")
                    yield Request(url=url, callback=self.parse_page_content)

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        # 文章标题
        title = soup.title.text

        # 发布时间
        pub_time_row = soup.find(class_="date").find("time").text
        pub_time_list = pub_time_row.split('.')
        pub_time_year = pub_time_list[2].split(' ')[0]
        pub_time = f"{pub_time_year}-{pub_time_list[1]}-{pub_time_list[0]}"

        # 文章类型
        try:
            category_list = soup.find(class_="breadcrumb").find_all("span")
            category1 = ""
            category2 = ""
            t = int(1)  # t是计数器，因为类型是有三部分构成，最后一部分是文章名称，所以只存取前两部分即可，用计数器做判断
            for i in category_list:
                if t==1:
                    category1 = i.text
                    t+=1
                elif t==2:
                    category2 = i.text
                    t+=1
        except:
            category1 = category2 = None

        # 文章图片
        img = []
        pic_list = soup.find_all(class_="img")
        for i in pic_list:
            try:
                pic = i.find("img").get("data-src")
            except:
                try:
                    pic = i.find("img").get("src")
                except:
                    pic = None
            if pic!=None:
                img.append(pic)

        # 文章简介
        abstract = soup.find(class_="spot-title").text

        # 文章内容
        body = ""
        try:
            body_row = soup.find(class_="content type1").text
            body = body_row.strip()
            body = body.replace('\n', '')
        except:
            body_row = soup.find_all(class_="description")
            for i in body_row:
                body += i.text
                body += '\n'

        item = NewsItem()
        item['title'] = title
        item['category1'] = category1
        item['category2'] = category2
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = img
        yield item