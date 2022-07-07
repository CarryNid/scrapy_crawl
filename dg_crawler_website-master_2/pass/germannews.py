from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from bs4 import BeautifulSoup

class GermannewsSpider(BaseSpider):  # author：田宇甲 动态超短
    name, website_id, language_id, is_http, start_urls = 'germannews', 1796, 1898, 1, [f'http://german.news.cn/ds_{i}.json' for i in ['5a16c54fed0d45e191af368ac1710d18', '53edeacb8a4f486fbb6940bf8ca60196', 'd8107750d011458cb9f642326fec0881', 'b7952637fe05403592520fe081ffb1df', '0cc44f98ae4847a1b617a43b95c70e17', 'c566a70c79134e46a0006e33dce816e7', '3727980c5070428984ac90efec014555', 'f6b54dd2d1f140a6adec048ea70ff848', '231852e133aa4b1e965ea91ccf6e2fd2']]

    def parse(self, response):
        for i in response.json()['datasource']:
            if self.time is None or DateUtil.formate_time2time_stamp(i['publishTime']) >= int(self.time):
                yield scrapy.http.request.Request('http://german.news.cn/'+i['publishUrl'], callback=self.parse_item, meta={'pub_time_': i['publishTime'], 'title_': i['title'], 'abstract_': i['summary'], 'images_': [('http://german.news.cn/'+i['titleImages'][0]['imageUrl'] if i['titleImages'] != [] else '')], 'category1_': i['keywords'].split(',')[0]})

    def parse_item(self, response):
        item, soup = NewsItem(), BeautifulSoup(response.text, 'html.parser')
        item['title'], item['category1'], item['body'], item['abstract'], item['pub_time'], item['images'] = response.meta['title_'], response.meta['category1_'], soup.select_one(' #detailContent').text, response.meta['abstract_'], response.meta['pub_time_'], response.meta['images_']
        yield item
