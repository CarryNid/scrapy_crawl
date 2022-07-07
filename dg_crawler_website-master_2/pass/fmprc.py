import scrapy
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

# author:陈宣齐 2022.1.14
class FmprcSpider(BaseSpider):
    name = 'fmprc'
    website_id = 69
    language_id = 1809
    # allowed_domains = ['fmprc.gov']
    start_urls = ['https://www.fmprc.gov.cn/web/zwbd_673032/wshd_673034/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('div',class_='bd').find_all('li'):
            url = i.find('a').get('href').split('/')[1]
            if url == '':
                yield scrapy.Request(url='https://www.fmprc.gov.cn/web/zwbd_673032/wshd_673034/',callback=self.parse_2)
            else:
                yield scrapy.Request(url='https://www.fmprc.gov.cn/web/zwbd_673032/' + url , callback=self.parse_2)

    def parse_2(self,response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.select('div.newsBd > ul > li'):
            news_url = ''
            for a in i.find('a').get('href').split('/')[1:]:
                news_url += a + '/'
            if 'index_' in response.url:
                yield scrapy.Request(url=response.url.split('index_')[0] + news_url.strip('/') , callback=self.parse_3)
            else:
                yield scrapy.Request(url=response.url + news_url.strip('/') , callback=self.parse_3)
        if response.url != 'https://www.mfa.gov.cn':
            last_time = soup.select('div.newsBd > ul > li')[-1].text.split('（')[-1].strip('）   ') + ' 00:00:00'
            if self.time is not None:
                if self.time < DateUtil.formate_time2time_stamp(last_time):
                    if response.meta.get('page') is not None:
                        page = int(response.meta['page']) + 1
                        meta = {
                            'page': str(page)
                        }
                        yield scrapy.Request(url=response.url.split('index_')[0] + 'index_' + str(page) + '.shtml', callback=self.parse_2,
                                             meta=meta)
                    else:
                        meta = {
                            'page': '1'
                        }
                        yield scrapy.Request(url=response.url + 'index_1.shtml', callback=self.parse_2, meta=meta)
                else:
                    self.logger.info("超时了")
            else:
                # 不是第一页
                if 'shtml' in response.url:
                    page = int(response.meta['page']) + 1
                    meta = {
                        'page': str(page)
                    }
                    yield scrapy.Request(url=response.url.split('index_')[0] + 'index_' + str(page) + '.shtml', callback=self.parse_2,
                                         meta=meta)
                else:
                    meta = {
                        'page': '1'
                    }
                    yield scrapy.Request(url=response.url + 'index_1.shtml', callback=self.parse_2, meta=meta)


    def parse_3(self,response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        if response.url != 'https://www.mfa.gov.cn/':
            if soup.find('div',class_='news-title') is not None:
                item['title'] = soup.find('div',class_='news-title').text
            elif soup.find('div',id='News_Body_Title') is not None:
                item['title'] = soup.find('div',id='News_Body_Title').text
            item['body'] = ''
            item['abstract'] = soup.select('div#News_Body_Txt_A  p')[0].text
            for i in soup.select('div#News_Body_Txt_A  p'):
                item['body'] += i.text
            item['images'] = []
            new_url = ''
            for a in response.url.split('/')[:-1]:
                new_url += a + '/'
            for i in soup.select('div#News_Body_Txt_A  img'):
                item['images'].append(new_url + i.get('src'))
            if soup.find('div',class_='break') is not None:
                item['category1'] = soup.select('div.break a')[-2].get('title')
                item['category2'] = soup.select('div.break a')[-1].get('title')
            elif soup.find('div',class_='nav') is not None:
                item['category1'] = soup.select('div.nav a')[-2].get('title')
                item['category2'] = soup.select('div.nav a')[-1].get('title')
            if soup.find('p',class_='time') is not None:
                item['pub_time'] = soup.select('p.time > span')[-1].text + ':00'
            elif soup.find('span',id='News_Body_Time') is not None:
                item['pub_time'] = soup.select('span#News_Body_Time')[0].text + ':00'
            return item