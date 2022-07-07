from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
import datetime

#author: 蔡卓妍
class DailysabahSpider(BaseSpider):
    name = 'dailysabah'
    website_id = 1956
    language_id = 1866
    start_urls = ['https://www.dailysabah.com/']
    proxy = '02'

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        lists = soup.select(".menu_items")
        for i in lists:
            category1 = i.select_one("a").text.strip()
            for i in i.select("a")[1:]:
                news_url = i.get("href")
                category2 = i.text.strip()
                meta = {'category1': category1,'category2':category2}
                yield Request(url=news_url, meta=meta, callback=self.parse2)

    def parse2(self,response):
        soup = BeautifulSoup(response.text,"html.parser")
        news_url = 'https://www.dailysabah.com' + soup.select_one(".absolute_right_link a").get("href")
        yield Request(url=news_url, meta=response.meta, callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        try:
            flag = True
            last_time = datetime.datetime.strptime(soup.select(".widget_content")[-1].select_one(".date_text").text.strip(), '%b %d, %Y')
            if self.time is None or DateUtil.formate_time2time_stamp(str(last_time)) >= int(self.time):
                lists = soup.select(".widget_content")
                for i in lists:
                    response.meta['title'] = i.select_one("a").text.strip()
                    article = i.select_one("a").get("href")
                    response.meta['pub_time'] = datetime.datetime.strptime(i.select_one(".date_text").text.strip(), '%b %d, %Y')
                    if "/gallery/" in article:
                        pass
                    else:
                        yield Request(url=article, callback=self.parse_item, meta=response.meta)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:  # 翻页
                page = soup.select_one('.page_number.active').text
                if '&' in response.url:
                    next_page = response.url.replace(f'pgno={page}', f'pgno={int(page) + 1}')
                else:
                    next_page = response.url + str(f"&pgno={int(page) + 1}")
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info("no more pages")

    def parse_item(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        try:
            item['abstract'] = soup.select_one(".article_body p").text.strip()
            item['body'] = "\n".join(i.text.strip() for i in soup.select(".article_body p"))
        except:
            item['abstract'] = soup.select_one(".article_body").text.strip().split("\n")[0]
            item['body'] = "".join(i.replace("\r","\n") for i in (soup.select_one(".article_body").text.strip().split("\n")))
        item['images'] = [soup.select_one(".layout-ratio img").get("src")]
        item['pub_time'] = response.meta['pub_time']
        yield item