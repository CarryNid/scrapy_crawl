from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

Germany_MONTH = {
        'Januar': '01',
        'Februar': '02',
        'März': '03',
        'April': '04',
        'Mai': '05',
        'Juni': '06',
        'Juli': '07',
        'August': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Dezember': '12'}

# author : 梁智霖
class Destatis_deSpider(BaseSpider):
    name = 'destatis_de'
    website_id = 1677
    language_id = 1901 #德语
    #allowed_domains = ['destatis.de']
    start_urls = ['https://www.destatis.de/SiteGlobals/Forms/Suche/Presse/DE/Pressesuche_Formular.html']
    # is_http = 1 #若网站使用的是http协议，需要加上这个类成员(类变量)
    # 这个网站网络有点问题，报403比较频繁，文章没有问题

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('span.c-filter__dropdown > a.c-filter__item')[0:42]
        for category1 in categories:
            category_url = category1.get('href')
            category1_text = category1.text.split('(')[0]
            yield Request(url='https://www.destatis.de/' + category_url, callback=self.parse_page,
                          meta={'category1': category1_text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        try:
            if self.time is not None:
                tt = soup.select('div.column.small-12.medium-7.large-8 > h3 > a > span')[-1].text.split(' ')
                ttr = tt[-3].split('.')[0]
                if int(ttr) < 10:
                    ttr = "0" + ttr
                last_time = tt[-1] + "-" + Germany_MONTH[tt[-2]] + "-" + str(ttr) + " 00:00:00"
            if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
                articles = soup.select('div.column.small-12.medium-7.large-8')
                for article in articles:
                    article_url = article.select_one('h3 > a').get('href')
                    title = article.select_one('h3 > a').text.lstrip()
                    tt2 = soup.select_one('h3 > a > span').text.split(' ')
                    ttr2 = tt2[-3].split('.')[0]
                    if int(ttr2) < 10:
                        ttr2 = "0" + ttr2
                    pub_time = tt2[-1] + "-" + Germany_MONTH[tt2[-2]] + "-" + str(ttr2) + " 00:00:00"
                    abstract = soup.select_one('div.column.small-12.medium-7.large-8 > p').text
                    yield Request(url='https://www.destatis.de/' + article_url , callback=self.parse_item, meta={'category1': response.meta['category1'],'title': title,'pub_time': pub_time,'abstract':abstract})
            else:
                self.logger.info("时间截止")
            if flag:
                if soup.select('div.navIndex > ul > li> a').text:
                    next_page = 'https://www.destatis.de/' + soup.select('div.navIndex > ul > li> a')[-1].get('href')
                    # print(next_page)
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info('no more page.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = '' #该网站文章没有src图片，部分文章有表格数据和动态图片
        try:
            item['body'] = ''.join(
                paragraph.text.lstrip() for paragraph in soup.select('div.content > p')  if
                 paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        item['abstract'] = response.meta['abstract']
        yield item