from crawler.spiders import BaseSpider
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http.request import Request

# author : 赖晓杰
from utils.date_util import DateUtil


class ssezSpiderSpider(BaseSpider):
    name = 'ssez'
    website_id = 1889
    language_id = 1813
    start_urls = ['http://ssez.com/index.asp']
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        new_url = 'http://ssez.com/' + (soup.select('.ajxmw1 > ul > li')[3].a)['href']
        yield Request(url = new_url, callback=self.t_parse)

    def t_parse(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        lst = []
        for i in range(1, int(soup.select('div.digg4 > a')[-3].text) + 1):
            lst.append('http://ssez.com/News.asp?page={}'.format(i) + '&None=3')
        for url in lst:
            yield Request(url = url, callback=self.parse2)

    def parse2(self,response):
        soup = BeautifulSoup(response.text,'lxml')
        last_time = soup.find_all('td', width="100", style="border-bottom:1px solid #e7e7e7")[-1].text + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for item in soup.find_all('td', height="25", style="border-bottom:1px solid #e7e7e7"):
                detial_url = 'http://ssez.com/News.asp' + item.a['href']
                yield Request(url=detial_url, callback=self.parse3, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse3(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['title'] = soup.select_one('td > strong').text
        item['category1'] = str(soup.select(' div > font')[2].text)[6:10]
        content = soup.find('td',id="content").text
        item['body'] = content
        item['abstract'] = str(content)[:content.find('。') + 1]
        t = soup.find_all('td', align="center")[1].text
        item['pub_time'] = t.split(' ')[2].replace('发布时间：', '')
        if str(soup.find('img', galleryimg="no")) == 'None':
            pass
        else:
            item['images'] = ['http://ssez.com/' + soup.find('img',galleryimg="no")['src'][1:], ]
        yield item
