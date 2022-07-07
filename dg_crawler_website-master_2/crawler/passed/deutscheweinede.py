from copy import deepcopy
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import time

# author：欧炎镁
class DeutscheweinedeSpider(BaseSpider):
    name = 'deutscheweinede'
    # allowed_domains = ['deutscheweine.de']
    start_urls = ['http://deutscheweine.de/']

    website_id = 1762
    language_id = 1846

    def parse(self, response):
        # 新闻在这两个页面中
        li_obj_link = response.css('ul.nav.navbar-nav li#item3,li#item99')
        for li_obj in li_obj_link:
            page_link = li_obj.css('ul > li a::attr(href)').extract()[0]
            meta = {
                'data':{'category1': li_obj.css('ul > li a::text').extract()[0]}
            }
            yield scrapy.Request(page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        div_obj_n = response.css('div.news-list-view div.csc-default.article.articletype-0')
        flag = True
        if self.time is None:
            for div_obj in div_obj_n:
                response.meta['data']['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('div.news-list-date::text').extract_first().strip(), "%d.%m.%Y"))
                response.meta['data']['title'] = div_obj.css('h2::text').extract_first()
                response.meta['data']['category2'] = div_obj.css('div.category::text').extract_first()
                abstract_link = div_obj.css('div.csc-textBody')
                response.meta['data']['abstract'] = abstract_link.css('p::text').extract_first()
                content_link = abstract_link.css('a::attr(href)').extract_first()
                yield scrapy.Request(content_link, callback=self.parse_item, meta=deepcopy(response.meta))

        else:
            last_pub = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj_n[-1].css('div.news-list-date::text').extract_first().strip(), "%d.%m.%Y"))
            if self.time < DateUtil.formate_time2time_stamp(last_pub):
                for div_obj in div_obj_n:
                    response.meta['data']['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('div.news-list-date::text').extract_first().strip(), "%d.%m.%Y"))
                    response.meta['data']['title'] = div_obj.css('h2::text').extract_first()
                    response.meta['data']['category2'] = div_obj.css('div.category::text').extract_first()
                    abstract_link = div_obj.css('div.csc-textBody')
                    response.meta['data']['abstract'] = abstract_link.css('p::text').extract_first()
                    content_link = abstract_link.css('a::attr(href)').extract_first()
                    yield scrapy.Request(content_link, callback=self.parse_item, meta=deepcopy(response.meta))
            else:
                self.logger.info("时间截止")
                flag = False

        # # 翻页
        if flag:
            try:
                next_page_link = response.css('li.last.next a::attr(href)')[-1].extract()
                yield scrapy.Request(next_page_link, callback=self.parse_page, meta=deepcopy(response.meta))
            except:
                pass

    def parse_item(self, response):
        # 第一段和其余段的clss都是csc-textBody 不止取p标签的，其他ul/table等标签的数据也取
        content_other = response.css('div.row > div.col-lg-6.col-md-6.col-sm-12.col-xs-12 div.csc-textBody').xpath('string(.)').extract()
        if content_other:
            # 每一段以“\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t”开头，以其分割然后在拼起来
            content = ''.join(content_other).split('\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')
            content = [i.strip() for i in content]
            response.meta['data']['body'] = '\n\t'.join(content).strip()
        else:
            response.meta['data']['body'] = ''
        try:
            img_list = response.css(
                'div.row div.col-lg-6.col-md-6.col-sm-12.col-xs-12:nth-child(2) div.xm-responsive-images img:not([data-srcset])::attr(src)').extract()
            response.meta['data']['images'] = ['https://www.deutscheweine.de' + img for img in img_list]
        except:
            response.meta['data']['images'] = []
        if (not response.meta['data']['abstract'] or response.meta['data']['abstract'].strip() == '') and response.meta['data']['body'] != '':
            response.meta['data']['abstract'] = response.meta['data']['body'].split('.')[0] + '.'
        item = NewsItem(response.meta['data'])
        yield item

