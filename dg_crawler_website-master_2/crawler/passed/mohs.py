from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from bs4 import BeautifulSoup
from scrapy.http.request import Request
import re
from common import date

# author: 蔡卓妍
class MohsSpider(BaseSpider):
    name = 'mohs'
    website_id = 1362
    language_id = 1797
    start_urls = ['https://www.mohs.gov.mm/']

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        new_url = 'https://www.mohs.gov.mm/' + soup.select_one('#topMain > li:nth-child(3) > a').get('href')
        yield Request(url=new_url,callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        try:
            flag = True
            time = soup.select('.column-date')[-1].text.split()
            last_time = f"20{time[2]}-{date.ENGLISH_MONTH[time[1]]}-{time[0]} 00:00:00"
            if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
                articles = soup.select('#page-content > div > div')
                for i in articles:
                    article = 'https://www.mohs.gov.mm' + i.select_one('.blog-column-img > a').get('href')
                    title = i.select_one('.blog-column-title').text
                    try:
                        t = re.findall(r'[(](.*?)[)]',title)[-1].split(' ')
                        day = f"{t[0].split('-')[2].strip(',')}-{t[0].split('-')[1]}-{t[0].split('-')[0]}"
                        if 'AM' in t:
                            pub_time = f"{day} 0{int(t[1][0])}:00"
                        elif 'PM' in t:
                            pub_time = f"{day} {str(int(t[1][0])+12)}:{int(t[1][-2])}{int(t[1][-1])}:00"
                        else:
                            time = i.select_one('.column-date').text.split()
                            pub_time = f"20{time[2]}-{date.ENGLISH_MONTH[time[1]]}-{time[0]} 00:00:00"
                    except:
                        time = i.select_one('.column-date').text.split()
                        pub_time = f"20{time[2]}-{date.ENGLISH_MONTH[time[1]]}-{time[0]} 00:00:00"
                    meta = {'title': i.select_one('.blog-column-title').text,'abstract': i.select_one('.blog-column-desc > p').text, 'pub_time': pub_time}
                    yield Request(url=article,meta=meta,callback=self.parse_item)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                if 'pagesize=9' == response.url.split('&')[-1]:
                    next_page = 'https://www.mohs.gov.mm/main/content/new/list?pagesize=9&pagenumber=2'
                else:
                    page = response.url.split('pagenumber=')[-1]
                    next_page = response.url.replace(f'pagenumber={page}', f'pagenumber={int(page) + 1}')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info("no more pages")

    def parse_item(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            item = NewsItem()
            item['title'] = response.meta['title']
            item['category1'] = 'news'
            if soup.select('.single-blog-text-area div p') != None: # body有部分只有图片
                item['body'] = '\n'.join(i.text.strip() for i in soup.select('.single-blog-text-area p'))
            else:
                item['body'] = 'images'
            item['abstract'] = response.meta['abstract']
            item['pub_time'] = response.meta['pub_time']
            item['images'] = [', '.join(i.get('src') for i in soup.select('.single-blog-text-area img'))]
            yield item
        except:#有少部分会报错
            pass