from crawler.spiders import BaseSpider
from bs4 import BeautifulSoup
from crawler.items import *
import datetime
import scrapy
from utils.date_util import DateUtil
from scrapy.http.request import Request

#author: 蔡卓妍
#有部分内容含有表情包（编码问题？）存不进数据库
def p_time(ti):
    return datetime.datetime.strptime(ti.strip(), '%d.%m.%Y')
class IstanbulSpider(BaseSpider):
    name = 'istanbul'
    website_id = 1834
    language_id = 2227
    start_urls = ["http://www.istanbul.gov.tr/haberler",
                  "http://www.istanbul.gov.tr/validen-haberler"]
    form_data = {"page": "1",
                 "OrderByAsc": "true",
                 "ContentCount": "8"}
    post_url = "http://www.istanbul.gov.tr/ISAYWebPart/ContentList/DahaFazlaYukle"
    is_http = 1
    proxy = '02'

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select_one(".page-title span").text
        yield Request(url=response.url,callback=self.parse2,meta={"category1":category1})

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        last_time = p_time(soup.select(".cardDate")[-1].text)
        if self.time is None or DateUtil.formate_time2time_stamp(str(last_time)) >= int(self.time):
            lists = soup.select(".col .card-stretch")
            for i in lists:
                response.meta['title'] = i.select_one(".card-title").text
                response.meta['pub_time'] = p_time(i.select_one(".cardDate").text)
                response.meta['img'] = "http://www.istanbul.gov.tr" + i.select_one(".card-img-top").get("src")
                if "www." in i.select_one(".news-card-horizontal").get("href"):
                    article = "http:" + i.select_one(".news-card-horizontal").get("href")
                else:
                    article = "http://www.istanbul.gov.tr" + i.select_one(".news-card-horizontal").get("href")
                yield Request(url=article,meta=response.meta,callback=self.parse_item)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag: # 翻页post
            if response.meta['category1'] == 'Haberler':
                self.form_data["ContentTypeId"] = "KdmoMQh9rkXTVUpogJKQ2A=="
                self.form_data["page"] = str(int(self.form_data["page"]) + 1)
            else:
                self.form_data["ContentTypeId"] = "o5fJvbJx+4U3q5/Za5g7Ow=="
                self.form_data["page"] = str(int(self.form_data["page"]) + 1)
            yield scrapy.FormRequest(url=self.post_url, formdata=self.form_data, callback=self.parse2,meta=response.meta)

    def parse_item(self,response): #有一些title或body含有表情包 存不进数据库
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        try:
            item['title'] = response.meta['title']
            item['category1'] = response.meta["category1"]
            item['body'] = "\n".join(i.text.strip() for i in soup.find_all(style="font-family:Calibri,sans-serif"))
            item['abstract'] = soup.find(style="font-family:Calibri,sans-serif").text
            item['images'] = [response.meta['img']]
            item['pub_time'] = response.meta['pub_time']
            yield item
        except:
            pass