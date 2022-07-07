from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from bs4 import BeautifulSoup
from scrapy.http.request import Request
Month = {'Januari': '01',
         'Februari': '02',
         'Maret': '03',
         'April': "04",
         'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12'} # 印尼语月份

#author: 蔡卓妍
# check:why
#有小小的一部分有时报status:400
class MaritimSpider(BaseSpider):
    name = 'maritim'
    website_id = 78
    language_id = 1952
    start_urls = ['https://maritim.go.id/artikel/',
                  'https://maritim.go.id/berita-deputi/',
                  'https://maritim.go.id/siaran-pers/',
                  'https://maritim.go.id/foto/',
                  'https://maritim.go.id/berita/infografis/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        flag = True
        ltime = soup.select('.article-content-wrap')[-1].select_one('span').text.split(',')[1].strip().split()
        last_time = ltime[2] + '-' + Month[ltime[1]] + '-' + ltime[0] + ' ' + '00:00:00'
        try:
            if self.time is None or DateUtil.formate_time2time_stamp(str(last_time)) >= int(self.time):
                category1 = response.url.split('/')[3].strip()
                lists = soup.select('.entire-meta-link')
                for i in lists:
                    news_url = i.get('href')
                    meta = {'category1': category1}
                    yield Request(url=news_url, meta=meta, callback=self.parse_items)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                p = response.url.split('/')[-2]
                if 'page/' not in response.url:
                    next_page = response.url + 'page/2'
                else:
                    next_page = response.url.replace(str(p), f"{str(int(p) + 1)}")
                yield Request(url=next_page, callback=self.parse)
        except:
            self.logger.info("no more pages")

    def parse_items(self,response):
        item = NewsItem()
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = soup.select_one('.entry-title').text.strip()
        item['category1'] = response.meta['category1']
        ptime = soup.find(id="single-below-header").select_one('.meta-date').text.split(',')[1].strip().split()
        item['pub_time'] = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
        item['body'] = "\n".join(i.text.strip() for i in soup.select('p'))
        if 'No.SP' in soup.select_one('p').text:
            item['abstract'] = soup.select('p')[1].text
        else:
            item['abstract'] = soup.select_one('p').text
        item['images'] = [i.get('src') for i in (soup.select('#gallery-1 img') + soup.select('.post-featured-img img'))]
        yield item
