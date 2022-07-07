from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

Tai_MONTH = {
        'ม.ค.': '01',
        'ก.พ.': '02',
        'มี.ค': '03',
        'เม.ย.': '04',
        'พ.ค.': '05',
        'มิ.ย.': '06',
        'ก.ค.': '07',
        'ส.ค.': '08',
        'ก.ย': '09',
        'ต.ล.': '10',
        'พ.ย.': '11',
        'ธ.ค.': '12'}


# author : 梁智霖
class PosttodaySpider(BaseSpider):
    name = 'posttoday'
    website_id = 1575
    language_id = 2208
    #allowed_domains = ['posttoday.com']
    start_urls = ['https://www.posttoday.com']
    # is_http = 1
    #若网站使用的是http协议，需要加上这个类成员(类变量)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('#mainheader > div > nav > ul > li > a')[1:7]
        for category1 in categories:
            category_url = category1.get('href')
            yield Request(url=category_url, callback=self.parse_url, meta={'category1': category1.text})

    def parse_url(self, response):
        request_url1 = response.url
        response.meta['request_url'] = request_url1
        page_number = 1
        response.meta['page_number'] = page_number
        request_url = request_url1 + '?page=' + str(page_number) + '&pageoffset=7&pagelimit=6'
        yield scrapy.Request(request_url, meta=response.meta, callback=self.parse_page, dont_filter=True)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        if self.time is not None:
            tt = soup.select('div.item-detail > div')[-1].text.split(' ')
            last_time = str(int(tt[3]) - 543) + "-" + Tai_MONTH[tt[2]] + "-" + str(tt[1]) + " " + str(tt[5]) + ":00"

        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            articles = soup.select('div > div.item-detail > h6 > a')
            for article in articles:
                article_url = article.get('href')
                title = article.text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'],'title': title})
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            try:
                response.meta['page_number'] = response.meta['page_number'] + 1
                request_url1 = response.meta['request_url']
                request_url = 'https://www.posttoday.com/list_content/' + request_url1.split('/')[3].split('?')[0] + '?page=' +str(response.meta['page_number']) + '&pageoffset=7&pagelimit=6'
                # page_num = int(response.url.split('page=')[1].split('&')[0]) //法2
                yield Request(url=request_url, callback=self.parse_page, meta=response.meta)
            except:
                self.logger.info(response.url + ' has no the next page.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.article-content > p')
             if paragraph.text != '' and paragraph.text != ' '])
        # item['abstract'] = '\n'.join(
        #     [paragraph.text.strip() for paragraph in soup.select('div.article-content > div.article-intro')
        #      if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]

        try:
            item['images'] = [img.get('src') for img in soup.select('div.section-article.border-color > article > picture > img')]
        except:
            item['images'] = ''

        ttt = soup.select_one('article > div.article-headline.border-color > div').text.split(' ')
        pub_time = str(int(ttt[3]) - 543) + "-" + Tai_MONTH[ttt[2]] + "-" + str(ttt[1]) + " " + str(ttt[5]) + ":00"
        item['pub_time'] = pub_time
        yield item

