# 此文件包含的头文件不要修改
from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
import re
import requests

# author: 陈宝胜
# 将爬虫类名和name字段改成对应的网站名
class BernamaSpider(BaseSpider):
    name = 'bernama'
    website_id = 138  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://www.bernama.com/en/general/covid-19.php',
                  'https://www.bernama.com/en/general/index.php',
                  'https://www.bernama.com/en/politics/index.php',
                  'https://www.bernama.com/en/b_focus/index.php',
                  'https://www.bernama.com/en/features/index.php',
                  'https://www.bernama.com/en/meta/index.php',
                  'https://www.bernama.com/en/press/index.php',
                  'https://www.bernama.com/en/region/index.php?s=1',
                  'https://www.bernama.com/en/region/index.php?s=2',
                  'https://www.bernama.com/en/region/index.php?s=3',
                  'https://www.bernama.com/en/region/index.php?s=4',
                  'https://www.bernama.com/en/region/index.php?s=5',
                  'https://www.bernama.com/en/region/index.php?s=6',
                  'https://www.bernama.com/en/business/pemerkasa.php',
                  'https://www.bernama.com/en/crime_courts/index.php',
                  'https://www.bernama.com/en/business/index.php',
                  'https://www.bernama.com/en/market/index.php'
                  ]
    # sql = {  # sql配置
    #     'host': '192.168.235.162',
    #     'user': 'dg_admin',
    #     'password': 'dg_admin',
    #     'db': 'dg_crawler'
    # }
    # sql = {  # sql配置
    #     'host': '121.36.242.178',
    #     'user': 'dg_cbs',
    #     'password': 'dg_cbs',
    #     'db': 'dg_test_source'
    # }
    no_category = {
        'thoughts', 'infographics', 'videos'
    }

    def get_time(self, url):
        # 获取时间戳
        soup = BeautifulSoup(requests.get(url).text)
        return Util.format_time3(str(datetime.strptime(soup.select(".col.pt-3 .row .row .col-6.mt-3")[1].text.strip().rsplit(" ", 1)[0], "%d/%m/%Y %H:%M")))


    # 这是类初始化函数，用来传时间戳参数

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for a in soup.select(".container-fluid.px-0")[2].select(".col-sm-12.col-md-12.col-lg-12")[1].select("h6 a"):
            news_url = response.url.rsplit("/", 1)[0]+'/'+a.get("href")
            yield scrapy.Request(news_url, callback=self.parse_detail)
        next_page = response.url.rsplit("/", 1)[0]+'/'+soup.select("li.page-item a")[-1].get("href") if soup.select("li.page-item > a > .fa.fa-chevron-right") else None
        LastTimeStamp = self.get_time(news_url)
        if self.time is None or LastTimeStamp >= self.time:
            if next_page:
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                self.logger.info("该目录已经到底")
        else:
            self.logger.info("时间截止")

    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['pub_time'] = datetime.strptime(soup.select(".col.pt-3 .row .row .col-6.mt-3")[1].text.strip().rsplit(" ", 1)[0], "%d/%m/%Y %H:%M")
        item['title'] = soup.select_one(".container-fluid.px-0 .row h1.h2").text.strip()
        item['images'] = [img.get("data-src") for img in soup.select("#topstory .carousel-inner img")]
        item['category1'] = soup.select_one(".row .col-12.col-sm-12.col-md-12.col-lg-8 span").text.strip()
        item['category2'] = None
        item['body'] = "\n".join(p.text.strip() for p in soup.select(".col-12.mt-3.text-dark.text-justify > p"))
        item['abstract'] = item['body'].split("\n", 1)[0]
        item['website_id'] = self.website_id
        item['language_id'] = self.language_id
        item['request_url'] = response.request.url
        item['response_url'] = response.url
        item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        yield item