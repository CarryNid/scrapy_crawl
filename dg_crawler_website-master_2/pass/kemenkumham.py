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
class KemenkumhamSpider(BaseSpider):
    name = 'kemenkumham'
    website_id = 89
    language_id = 1952
    start_urls = ['https://www.kemenkumham.go.id/berita',
                  'https://www.kemenkumham.go.id/berita/berita-pusat',#内容有点久远
                  'https://www.kemenkumham.go.id/berita/berita-media'] #内容有点久远

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        ltime = soup.select('.article-text .create')[-1].text.strip().split()
        last_time = ltime[2] + '-' + Month[ltime[1]] + '-' + ltime[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(str(last_time)) >= int(self.time):
            lists = soup.select('.article-text')
            for i in lists:
                title = i.select_one('header h2 a').text.strip()
                news_url = 'https://www.kemenkumham.go.id' + i.select_one('header h2 a')['href']
                ptime = i.select('span')[1].text.strip().split()
                pub_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' 00:00:00'
                meta = {'pub_time': pub_time, 'title': title}
                yield Request(url=news_url, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = 'https://www.kemenkumham.go.id' + soup.select('.pagenav')[-2]['href']
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response): #有一些是图片集
        item = NewsItem()
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = 'berita'
        item['pub_time'] = response.meta['pub_time']
        try:
            if soup.select_one('p span') != None:
                if soup.select_one('p span').text.strip() == '':
                    item['abstract'] = soup.select('.item-page p span')[1].text.strip()
                else:
                    item['abstract'] = soup.select_one('.item-page p span').text.strip()
                item['body'] = "\n".join(i.text.strip() for i in soup.select('p span'))
            else:
                item['body'] = "\n".join(i.text.strip() for i in (soup.select('div strong') + soup.select('.item-page p')))
                try:
                    item['abstract'] = soup.select_one('div strong').text.strip()
                except:
                    if soup.select_one('.item-page p').text.strip() == '':
                        item['abstract'] = soup.select('.item-page p')[1].text.strip()
                    else:
                        item['abstract'] = soup.select_one('.item-page p').text.strip()
            try:
                item['images'] = ["https://www.kemenkumham.go.id"+i.get('src') for i in soup.select('p img')] \
                                 + [i.get('src') for i in soup.select('.item-page div >img')]
            except: #没有图片
                item['images'] = []
            yield item
        except: #极少部分新闻页面打开是空白的
            pass