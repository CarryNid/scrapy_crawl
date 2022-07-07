# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

#author: 吴元栩
class EnsonhaberSpider(BaseSpider):
    name = 'ensonhaber'
    website_id = 1958
    language_id = 2105
    type_list = ["otomobil","teknoloji","gundem","kralspor","kadin","emlak","politika","ekonomi","dunya","egitim-haberleri","3-sayfa","ic-haber","magazin","kultur-sanat","video","medya","yasam","tarih-haberleri","ipucu","kitap","seyahat"]
    start_urls = [f'https://www.ensonhaber.com/{type}?infinity=1&sayfa={i}'for type in type_list for i in range(1,190)]
    # start_urls = ['https://www.ensonhaber.com/seyahat?infinity=1&sayfa=1']
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if len(str(soup).strip()) == 0:
            return
        else:
            url_list = soup.find_all("a")
            for i in url_list:
                if str(i.get("href"))[0:5] != "https":
                    url = "https://www.ensonhaber.com/" + i.get("href")
                    yield Request(url=url, callback=self.parse_page_content)


    def parse_page_content(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')

        # 文章标题
        title = soup.find(class_="c-title").text.strip()

        # 文章时间
        pub_time_row_list = soup.find(class_="c-date").find_all("li")
        pub_time_row = pub_time_row_list[-1].text
        pub_time_list = pub_time_row.split('.')
        pub_time_month = pub_time_list[1]
        pub_time_year = pub_time_list[2].split(' ')[0]
        pub_time_day = pub_time_list[0].split(' ')[-1]
        pub_time = f"{pub_time_year}-{pub_time_month}-{pub_time_day}"

        # 文章类型
        category_list = soup.find(class_="bread").find_all("li")
        category1 = ""
        category2 = ""
        t = int(1)  # t是计数器，因为类型是有三部分构成，最后一部分是文章名称，所以只存取前两部分即可，用计数器做判断
        for i in category_list:
            if t == 1:
                category1 = i.text.strip()
                t += 1
            elif t == 2:
                category2 = i.text.strip()
                t += 1

        # 文章简介
        abstract = soup.find(class_="c-desc").text.strip()

        # 文章图片
        img = []
        try:
            pic = soup.find(class_="headline-img").find("img").get("src")
            img.append(pic)
        except:
            pic = soup.find(class_="detayResim").get("data-src")
            img.append(pic)

        # 文章内容
        body = soup.find(class_="body").text.strip()

        item = NewsItem()
        item['title'] = title
        item['category1'] = category1
        item['category2'] = category2
        item['body'] = body
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = img
        yield item
