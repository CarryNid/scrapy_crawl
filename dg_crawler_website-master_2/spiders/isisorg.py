# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


# author: 马颢源
ENGLISH_MONTH= {
        'January': '01',
        'February': '02',
        'Marvh': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }
class isisorgSpider(BaseSpider):
    name = 'isisorg'
    start_urls = ['https://www.isis.org.my/events/list']
    website_id = 706
    language_id = 2037

    def parse(self, response):
        li_list = response.xpath('//div[@id="tribe-events-footer"]/nav/ul/li')
        for i in li_list:
            url = i.xpath('./a/@href').get()
            category1 = i.xpath('./a/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if self.time is not None:
            time = response.xpath('//div[@class="tribe-event-schedule-details"]/span/text()').get().split()
            last_time = time[2] + '-' + ENGLISH_MONTH[time[1]] + '-' + time[0] + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            article_list = response.xpath('//div[@class="tribe-events-loop"]//div[contains(@id,"post")]')
            for i in article_list:
                url = i.xpath('./h3/a/@href').get()
                time = response.xpath('//div[@class="tribe-event-schedule-details"]/span/text()').get().split()
                pub_time = time[2] + '-' + ENGLISH_MONTH[time[1]] + '-' + time[0] + ' 00:00:00'
                response.meta['title'] = i.xpath('//h3[@class="tribe-events-list-event-title"]/a/text()').get()
                response.meta['abstract']=i.xpath('//div[@class="tribe-events-list-event-description tribe-events-content description entry-summary"]/p/text()').get()
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = response.xpath('//nav[@class="tribe-events-nav-pagination"]//a/@href').get()
            if next_page:
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)  # 默认回调给parse()
            else:
                 self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = response.meta['abstract']
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@id="post-20381"]//div[@class="column"]/p')])
        yield item