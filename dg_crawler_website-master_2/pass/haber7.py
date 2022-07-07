from crawler.spiders import BaseSpider
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from utils.date_util import DateUtil
# author: 蔡卓妍

def last_time(time):
    l_time = time.split()[0]
    if "DAKİKA ÖNCE" in time: # 分钟前
        la_time = int(DateUtil.time_ago(minute=int(l_time)))
    elif "SAAT ÖNCE" in time: # 小时前
        la_time = int(DateUtil.time_ago(hour=int(l_time)))
    elif "GÜN ÖNCE" in time: # 天前
        la_time = int(DateUtil.time_ago(day=int(l_time)))
    elif "HAFTA ÖNCE" in time: # 周前
        la_time = int(DateUtil.time_ago(week=int(l_time)))
    elif "AY ÖNCE" in time: # 月前
        la_time = int(DateUtil.time_ago(month=int(l_time)))
    else: # 年前
        la_time = int(DateUtil.time_ago(year=int(l_time)))
    return la_time

class Haber7Spider(BaseSpider):
    name = 'haber7'
    website_id = 1959
    language_id = 2227
    start_urls = ['https://www.haber7.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        lists = soup.select(".main-menu-item > a") + soup.select(".site-menu-list .items > a") + soup.select(".items gezelim > a")[:-1]
        for i in lists:
            news_url = i.get("href")
            category1 = i.get("title")
            meta = {'category1': category1,'category2':"None"} # 再分类有一些有 大部分没有
            yield Request(url=news_url, meta=meta, callback=self.parse_page)

    def parse_page(self,response): #分类较多
        soup = BeautifulSoup(response.text, 'html.parser')
        if response.meta["category1"] == "Spor Haberleri" and response.meta["category2"] == "None":  # 有再分类
            lists = soup.select(".site-header-bottom ul li a")
            for i in lists:
                news_url = i.get("href")
                category2 = i.get("title")
                response.meta["category2"] = category2
                yield Request(url=news_url, meta=response.meta, callback=self.parse_page)
        elif response.meta["category1"] == "Seyahat Haberleri": pass # 内容重复
        elif response.meta["category1"] == "Ekonomi Haberleri" \
                or response.meta["category1"] == "Son Dakika Haberleri" \
                or response.meta["category1"] == "Otomobil Haberleri"\
                or response.meta["category1"] == "Emlak Haberleri":
                #没有再分类 但结构与else里的不同，页面内没有时间、没有翻页
            lists = soup.select(".main-content a")
            for i in lists:
                try:
                    article = i.get("href")
                    response.meta['title'] = i.get("title")
                    if i.select_one("img") and i.select_one("img").get("data-lazy") != None:
                        response.meta['img'] = i.select_one("img").get("data-lazy")
                    elif i.select_one("img") and i.select_one("img").get("data-original") != None:
                        response.meta['img'] = i.select_one("img").get("data-original")
                    else:
                        response.meta['img'] = i.select_one("img").get("src")
                    yield Request(url=article, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else: # 具体的时间在新闻页面内
            try:
                flag = True
                last_time_ = last_time(soup.select(".infinite-item a")[-1].select_one(".date").text)
                if self.time is None or last_time_ >= int(self.time):
                    lists = soup.select(".infinite-item a")
                    for i in lists:
                        article = i.get("href")
                        response.meta['title'] = i.get("title")
                        if i.select_one("img") and i.select_one("img").get("data-lazy") != None:
                            response.meta['img'] = i.select_one("img").get("data-lazy")
                        elif i.select_one("img") and i.select_one("img").get("data-original") != None:
                            response.meta['img'] = i.select_one("img").get("data-original")
                        else:
                            response.meta['img'] = i.select_one("img").get("src")
                        yield Request(url=article, meta=response.meta, callback=self.parse_item)
                else:
                    flag = False
                    self.logger.info("时间截止")
                if flag:#翻页
                    next_page = "https://" + response.url.split("/")[2] + soup.select_one(".pagination__next").get("href")
                    yield Request(url=next_page,callback=self.parse_page,meta=response.meta)
            except:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        try:
            item['title'] = response.meta["title"]
            item['category1'] = response.meta['category1']
            if response.meta['category2'] != "None": # category1是Spor Haberleri的有，其他没有
                item['category2'] = response.meta['category2']
            item['body'] = "\n".join(i.text.strip() for i in (soup.select("div.news-content > p")))
            item['abstract'] = soup.select_one(".spot").text
            time = soup.select_one("span.date-item.updated").text.split()
            item['pub_time'] = time[1][6:10] + '-' + time[1][3:5] + '-' + time[1][:2] + ' ' + time[2] + ':00'
            item['images'] = [response.meta['img']] + [i.get("src") for i in soup.select(".news-content > p > img")]
            yield item
        except: #有一些抓到的不是新闻的网址（视频之类的）会报错
            pass