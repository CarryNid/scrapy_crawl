from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

Tai_MONTH = {
        'ม.ค.': '01',
        'มกราคม': '01',
        'ก.พ.': '02',
        'กุมภาพันธ์': '02',
        'มี.ค': '03',
        'มีนาคม': '03',
        'เม.ย.': '04',
        'เมษายน': '04',
        'พ.ค.': '05',
        'พฤษภาคม': '05',
        'มิ.ย.': '06',
        'มิถุนายน': '06',
        'ก.ค.': '07',
        'กรกฎาคม': '07',
        'ส.ค.': '08',
        'สิงหาคม': '08',
        'ก.ย': '09',
        'กันยายน': '09',
        'ต.ล.': '10',
        'ตุลาคม': '10',
        'พ.ย.': '11',
        'พฤศจิกายน': '11',
        'ธ.ค.': '12',
        'ธันวาคม': '12'}


# author : 梁智霖
class News_thaipbs_or_thSpider(BaseSpider):
    name = 'news_thaipbs_or_th'
    website_id = 1587
    language_id = 2208
    #allowed_domains = ['news.thaipbs.or.th']
    start_urls = ['https://news.thaipbs.or.th/archive']
    # is_http = 1
    #若网站使用的是http协议，需要加上这个类成员(类变量)

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        # 一级目录下的新闻点击加载更多按钮点不开，故爬取所有新闻栏目下的新闻
        category1 = soup.select_one(" div.news-category-header > h1")
        yield Request(url=response.url,callback=self.parse_page,meta={'category1': category1.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        if self.time is not None:
            tsfm = soup.select_one(
                'article:nth-child(25) > div > div.item-content > div > span:nth-child(2)').text.split(' ')
            tnyr = soup.select_one(
                'article:nth-child(25) > div > div.item-content > div > span:nth-child(5)').text.split(' ')
            if int(tnyr[1]) < 10:
                tnyr[1] = "0" + tnyr[1]
            last_time = str(int(tnyr[3]) - 543) + "-" + Tai_MONTH[tnyr[2]] + "-" + str(tnyr[1]) + " " + str(tsfm[0]) + ":00"
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            articles = soup.select('#dropArea > article > div > a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': response.meta['category1']})
        else:
            self.logger.info("时间截止")
        if flag:
            try:
                next_page = "https://news.thaipbs.or.th" + soup.select_one('ul > li.next > a').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            except:
                self.logger.info(response.url + ' has no the next page.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = None
        #title 有两种格式
        try:
            title = soup.select_one('div.container > div > div.col-xs-12.col-md-8 > h1').text
            item['title'] = title
        except:
            title = soup.select_one('div.content-title-holder > div > div > header > h1').text
            item['title'] = title
        tsfm2 = soup.select_one('div.container > div > div:nth-child(1) > div > span:nth-child(2)').text
        tnyr2 = soup.select_one('div.container > div > div:nth-child(1) > div > span:nth-child(5)').text.split(' ')
        if int(tnyr2[1]) < 10:
            tnyr2[1] = "0" + tnyr2[1]
        pub_time = str(int(tnyr2[3]) - 543) + "-" + Tai_MONTH[tnyr2[2]] + "-" + str(tnyr2[1]) + " " + str(tsfm2) + ":00"
        item['pub_time'] = pub_time
        try:
            item['images'] = ["https:" + img.get('src') for img in soup.select('div.media-wrapper > img')]
        except:
            item['images'] = ''

        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.col-xs-12.col-md-9 > article > p')
             if paragraph.text != '' and paragraph.text != ' '])
        try:
            abstract = soup.select_one('div.content-subtitle-holder > div > div > div.col-xs-12.col-md-8 > div').text
            item['abstract'] = abstract
        except:
            abstract = item['body'].split('\n')[0]
            item['abstract'] = abstract
        yield item