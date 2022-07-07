# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
import json

#author: 吴元栩
class DonanimhaberSpider(BaseSpider):
    name = 'donanimhaber'
    website_id = 1970
    language_id = 2105
    start_urls = [f'https://www.donanimhaber.com/?sayfa={i}'for i in range(1,1000)]#该网站文章集合,其他栏目的文章在这个栏目也能找到

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url_list = soup.find_all(class_="medya")
        for i in url_list:
            url = "https://www.donanimhaber.com/" + i.find("a").get("href")
            yield Request(url=url, callback=self.parse_page_content)

    def parse_page_content(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')

        # 文章标题
        title = soup.find(class_="post-baslik").text.strip()

        # 发布时间
        pub_time_row = soup.find(class_="veri").get("datetime")
        pub_time = pub_time_row.split('T')[0]

        # 文章简介
        abstract = soup.find(class_="surmanset").text.strip()

        # 文章类型
        category = soup.find(class_="veri lnk").text.strip()

        # 文章图片
        img = []
        try:
            pic_list = soup.find_all(class_="dosya")
            for i in pic_list:
                pic = i.find("img").get("src")
                img.append(pic)
        except:
            img.append(None)

        # 文章内容
        body = soup.find(class_="kolon yazi").text.strip().replace('\n','')

        item = NewsItem()
        item['title'] = title
        item['category1'] = category
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = img
        yield item