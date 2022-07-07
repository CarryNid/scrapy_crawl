# encoding: utf-8
from bs4 import BeautifulSoup
from crawler.items import *
from crawler.spiders import BaseSpider
from scrapy.http.request import Request
from utils.date_util import DateUtil

class malaysiatodaySpider(BaseSpider):  # author:robot-2233
    name = 'malaysia-today'
    website_id = 168
    language_id = 1866
    start_urls = ['https://www.malaysia-today.net/archives/']  # 网站有屏蔽，只能获取到比较新的新闻
    proxy = '02'
    cookie = {
        'AID': 'AJHaeXIz2vggND5b7jUiQEEx1FwmEC4aNqIY2eTTWkoS1gXuNACivCBejOs',
        't_gid': 'c4190e06-7891-416a-a812-f62b9c8dbbba-tuct8853fac',
        'UID': '178c471d220a21930fd2d1e1656577005',
        '__gpi': 'UID=00000737403a479a:T=1656577005:RT=1656577005:S=ALNI_MY0txSVotEa_H4GpvaVrv1AQmV2pA',
        '_ga': 'GA1.2.662516877.1656577005',
        '__cf_bm': '734jk_o4CwKqyvhHViix.ABLjFx3pPVyayVCsdiqxs0-1656577010-0-AQCbZXCqrvyNFVLfJrw7wFLUCD5dvQTlDN23ndVxipP+wlGUdfdQXqUIoA7oG73K6SmrEA2BDGNT2wIdf7hedTy3YO/OEGuSmEV+qUH1IYnVQxMxOONbB4m8mskJGgu9RQ==',
        'fr': '00p7RHGH46x6S6Zbh..BivVvu...1.0.BivVvu.',
        '__stidv': '2',
        'fpestid': 'A_x5HCIVXHLD_18fbCTsmT3cspQsEOaxcDR4kcYwKsYd3ZEOJBfkU3mUEwXbC2lo9WbjBA',
        '_fbp': 'fb.1.1656577005168.854773534',
        '__stid': 'ZGEAAWK9W+0AAAAISjgPAw==',
        '_gat_gtag_UA_21031048_1': '1',
        'trc_cookie_storage': 'taboola%2520global%253Auser-id%3Dc4190e06-7891-416a-a812-f62b9c8dbbba-tuct8853fac',
        '__gads': 'ID=56d2b39a62b3af88-22271139d3d400be:T=1656577005:RT=1656577005:S=ALNI_MaRaRqFIOUpnxVhCX6rDJ9lFjgIyg',
        '_gid': 'GA1.2.1792644585.1656577005',
        '_cc_id': '9c92b1e23818d22da3e47f9ea2aba6c7',
        'panoramaId_expiry':'1656663860935'
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        "cookie": "_ga=GA1.2.662516877.1656577005; _gid=GA1.2.1792644585.1656577005; __gads=ID=56d2b39a62b3af88-22271139d3d400be:T=1656577005:RT=1656577005:S=ALNI_MaRaRqFIOUpnxVhCX6rDJ9lFjgIyg; __gpi=UID=00000737403a479a:T=1656577005:RT=1656577005:S=ALNI_MY0txSVotEa_H4GpvaVrv1AQmV2pA; _fbp=fb.1.1656577005168.854773534; trc_cookie_storage=taboola%2520global%253Auser-id%3Dc4190e06-7891-416a-a812-f62b9c8dbbba-tuct8853fac; fpestid=A_x5HCIVXHLD_18fbCTsmT3cspQsEOaxcDR4kcYwKsYd3ZEOJBfkU3mUEwXbC2lo9WbjBA; __cf_bm=734jk_o4CwKqyvhHViix.ABLjFx3pPVyayVCsdiqxs0-1656577010-0-AQCbZXCqrvyNFVLfJrw7wFLUCD5dvQTlDN23ndVxipP+wlGUdfdQXqUIoA7oG73K6SmrEA2BDGNT2wIdf7hedTy3YO/OEGuSmEV+qUH1IYnVQxMxOONbB4m8mskJGgu9RQ==; _cc_id=9c92b1e23818d22da3e47f9ea2aba6c7; panoramaId_expiry=1656663860935"}

    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse, headers=self.headers)

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .bs-vc-wrapper.wpb_wrapper article'):
            time_ = str(i.select_one(' .post-meta span time')).split('datetime="')[1].split('+')[0].replace('T', ' ')
            meta = {'pub_time_': time_, 'title_': i.select_one(' .title').text, 'category1_': i.select_one(' .post-meta a').text, 'abstract_': i.select_one(' .post-summary').text, 'images_': [str(i.select_one(' .featured.clearfix a')).split('url(')[1].split(');"')[0]]}
            if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):
                yield Request(url=i.select_one(' .title a').get('href'), callback=self.parse_item, meta=meta)
        if self.time is None or DateUtil.formate_time2time_stamp(time_) >= int(self.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'page' not in response.url:
                yield Request(response.url + 'page/2', meta=meta, headers=self.headers)
            else:
                yield Request(response.url.replace('page/' + response.url.split('page/')[1] + '/', 'page/' + str(int(response.url.split('page/')[1].strip('/')) + 1)+'/'), meta=meta, headers=self.headers)


    def parse_item(self, response):
        soup=BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:
            item['body'] = ''.join([i.text for i in soup.select(' .entry-content.clearfix.single-post-content p')])
        except:
            item['body'] = soup.select_one(' .content-detail-first').text
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item

