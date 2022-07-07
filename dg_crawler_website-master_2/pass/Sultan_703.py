# encoding: utf-8
from bs4 import BeautifulSoup

import utils.date_util
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
month = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12',
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    # 'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
    }


# Author:陈卓玮
class Sultan_703_Spider(BaseSpider):
    name = 'Sultan_703'
    website_id = 703
    language_id = 2036
    start_urls = ['https://owmpinternational.com/']

    def parse(self, response):
        column = ['projects','people','news']
        yield Request(url = self.start_urls[0]+column[0],callback=self.project_parser)
        yield Request(url = self.start_urls[0]+column[1],callback=self.people_parser)
        yield Request(url = "https://owmpinternational.com/news/page/1/?et_blog",callback=self.news_parser)


    def project_parser(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        project_list = soup.select('li')

        for project in project_list:
            imgs = []
            try:
                d_url = project.select_one('div.esg-entry-cover.esg-transition > a').get('href')
                imgs.append(project.select_one('img').get('data-lazysrc'))
                meta = {'imgs':imgs}
                yield Request(url = d_url,callback=self.project_detail_parser,meta=meta)
            except:
                continue

    def project_detail_parser(self, response):
        items = NewsItem()
        imgs = response.meta['imgs']
        soup = BeautifulSoup(response.text, 'html.parser')
        body = ''

        for img in soup.select('img'):
            try:
                imgs.append(img.get('data-lazy-src'))
            except:
                pass

        for p in soup.select('p'):
            body = body + p.text + '\n'

        title = soup.select_one('h1').text
        category1 = 'project'
        abstract = body.split('\n')[0]

        items['title'] = title
        items['category1'] = category1
        items['abstract'] = abstract
        items['body'] = body
        items['images'] = imgs
        items['pub_time'] = "2022-01-17"
        yield items

    def people_parser(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        imgs = []
        for i in soup.select('p > a'):
            d_url = i.get('href')
            imgs.append(i.select_one('img').get('data-lazy-src'))
            meta = {'imgs':imgs}
            yield Request(url = d_url,callback=self.people_detail_parser,meta = meta)

    def people_detail_parser(self,response):
        items = NewsItem()
        imgs = response.meta['imgs']
        soup = BeautifulSoup(response.text, 'html.parser')
        body = ''

        for i in soup.select('img'):
            imgs.append(i.select_one('src'))


        for p in soup.select('p'):
            body = body +p.text+'\n'

        items['title'] = soup.select_one('h3').text
        items['category1'] = "people"
        items['abstract'] = body.split('\n')[1]
        items['images'] = imgs
        items['body'] = body
        items['pub_time'] = "2022-01-17"

        yield items

    def news_parser(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        imgs = []
#--------------------------------------------------------
        articles = []
        urls=[]
        dates=[]
        for url in soup.select('article > h2 > a'):
            d_url = url.get('href')
            urls.append(d_url)

        for date in soup.select('article > p > span'):
            t = date.text.replace(',', '').split(' ')
            t[0] = month[t[0]]
            t = t[2] + '-' + t[0] + '-' + t[1]
            dates.append(t)



            t_stamp = utils.date_util.DateUtil.formate_time2time_stamp(t+' 00:00:00')


        for i in range(0,len(urls)):
            meta = {'url':urls[i],"date":dates[i],'imgs':imgs}

            yield Request(url=meta['url'], callback=self.news_detail_parser, meta=meta)

            if self.time == None or t_stamp >= self.time:
                page_num = int(response.url.split('page/')[1].split('/')[0])
                yield Request(url="https://owmpinternational.com/news/page/" + str(page_num + 1) + "/?et_blog",callback=self.news_parser)

#---------------------------------------------------------
        #
        # for i in soup.select('article'):
        #     print(i,end = '\n \n \n')
            # print(i.select_one('a').get('href'))
            # print(i.select_one('h2 > a').get('href'))
            # print(i.select_one('h2 > a').text)
            # print(i.select_one('p > span').text)

            # t[0] = month[t[0]]
            # t = t[2]+'-'+t[0]+'-'+t[1]

            # meta = {'imgs':imgs,'time':t}
            # print(d_url)
            # print(i.select_one('a.entry-featured-image-url > img').get('src'))
            # yield Request(url = d_url,callback=self.news_detail_parser,meta = meta)

        # if self.time == None or int(t[2]+t[0]+t[1]) >= int(self.time):
        #     # try:
        #     #     next_url = soup.select_one('.alignleft > a').get('href')
        #     #     print(next_url)
        #     page_num = int(response.url.split('page/')[1].split('/')[0])
        #     yield Request(url = "https://owmpinternational.com/news/page/"+ str(page_num+1)+ "/?et_blog")
        #     except:
        #         pass

    def news_detail_parser(self,response):
        items = NewsItem()
        body =''
        imgs = response.meta['imgs']
        soup = BeautifulSoup(response.text, 'html.parser')

        for i in soup.select('img'):
            if i.get('data-lazy-src') != None:
                imgs.append(i.get('data-lazy-src'))
        items['images'] = imgs
        items['title'] = soup.select_one('h1').text

        for b in soup.select('p'):
            body = body + b.text + '\n'

        items['body'] = body
        items['abstract'] = body.split('\n')[0]
        items['category1'] = 'news'
        items['pub_time'] = response.meta['date']
        yield items