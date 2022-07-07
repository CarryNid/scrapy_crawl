from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author : 武洪艳
class DofgovphSpider(BaseSpider):
    name = 'dofgovph'
    website_id = 1263
    language_id = 1866
    #  allowed_domains = ['www.dof.gov.ph/']
    start_urls = ['https://www.dof.gov.ph/category/news/']  # https://www.dof.gov.ph/category/news/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('#news-ul-list > li')
        if self.time is not None:
            t = articles[-1].select_one('span.date').text.split('/')
            last_time = '20' + t[2] + '-' + t[1] + '-' + t[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.select_one('span.date').text.split('/')
                pub_time = '20' + tt[2] + '-' + tt[1] + '-' + tt[0] + ' 00:00:00'
                article_url = article.select_one('a.learn-more.gold').get('href')
                title = article.select_one('h2').text
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1': 'news', 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            for i in range(3,283):
                if response.url == 'https://www.dof.gov.ph/category/news/':
                    next_page = 'https://www.dof.gov.ph/category/news/page/2/'
                else:
                    next_page = 'https://www.dof.gov.ph/category/news/page/' + str(i) +'/'
            # if soup.select_one('nav.custom-pagination .page-numbers.current + a') == None:
            #     self.logger.info("no more pages")
            # else:
            #     # next_page = soup.select_one('nav.custom-pagination a.next.page-numbers').get('href')
            #     next_page = soup.select_one('nav.custom-pagination .page-numbers.current + a').get('href')
                yield Request(url=next_page, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        # item['images'] = [img.get('src') for img in soup.select('.col-md-8 > article img') if
        #                   (img.get('src').split(':')[0] != 'data')]  #  无图片
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('#news-ul-list > li > p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
