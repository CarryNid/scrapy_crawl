# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

month = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }
# author:胡冠锋
#check:why
class DAWNSpider(BaseSpider):
    name = 'dawn'
    allowed_domains = ['www.dawn.com']
    start_urls = ['http://www.dawn.com']

    website_id = 358
    language_id = 1866

    def parse(self, response):
        li = response.xpath('/html/body/header/div[3]/div/nav/div/div/div[1]/div/a[2]')
        url = 'http://www.dawn.com' + li.xpath('./@href').get()
        category1 = li.xpath('./text()').get()
        yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if self.time is not None:
            time = response.xpath('//span[@class="timestamp--time  timeago"]/@title').get().split('T')
            last_time = time[0] + ' ' + time[1].split('+')[0]
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            article_list = response.xpath('//div[@class="tabs__pane active"]/article')
            for i in article_list:
                url = i.xpath('.//a[@class="story__link  "]/@href').get()
                time = response.xpath('//span[@class="timestamp--time  timeago"]/@title').get().split('T')
                #print(time)
                pub_time = time[0] + ' ' + time[1].split('+')[0]
                response.meta['title'] = i.xpath('.//a[@class="story__link  "]/text()').get().strip()
                response.meta['abstract'] = i.xpath('.//div[@class="story__excerpt      font-georgia  font-noto text-3.5 text-gray-700 overflow-hidden    pb-1  px-0  sm:px-2  mt-0"]/text()').get().strip()
                response.meta['images'] = i.xpath('.//picture/img/@src').get()
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")


    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        try:
            item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class="story__content  overflow-hidden    text-4  sm:text-4.5        pt-1  mt-1"]/p')])
        except:
            item['body'] = []
        item['images'] = response.meta['images']
        yield item
