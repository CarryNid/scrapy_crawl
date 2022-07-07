# encoding: utf-8
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup
from utils.date_util import DateUtil
import re
#author:陈嘉玲
class KohsantepheapdailySpider(BaseSpider):
    name = 'kohsantepheapdaily'
    website_id = 283
    language_id = 1982
    start_urls = ['https://kohsantepheapdaily.com.kh/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        li_list = soup.select('#main-nav > #main_nav_warp')
        for category in li_list[0]:
            try:
                category_url = category.a['href']
                if category_url == "https://kohsantepheapdaily.com.kh/tv":
                    continue
                meta = {'category1': category.text}
            except:
                continue
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        d_date = {'០': '0', '១': '1', '២': '2', '៣': '3', '៤': '4', '៥': '5', '៦': '6', '៧': '7',
                  '៨': '8', '៩': '9', 'ខែ': 'month', 'ឆ្នាំ': 'year',
                  '២០២២': '2022', 'មករា': '01', 'កុម្ភ': '02', 'មីនា': '03', 'មេសា': '04', 'ឧសភា': '05', 'មិថុនា': '06',
                  'កក្កដា': '07',
                  'សីហា': '08', 'កញ្ញា': '09', 'តុលា': '10', 'ិច្ឆិកា': '11', 'ធ្នូ': '12', 'ម៉ោង': '时间', 'ៈ': ''}

        if self.time is not None:
            t_ori = soup.find_all(attrs={'class': 'koh-icon-wrap icon-timer-inner'})
            for i in t_ori:
                time = i.get('title')
                time = time.replace('<br>', '').replace(':', ' ').split()
                for m in d_date:
                    for field in d_date:
                        field_value = d_date[field]
                        if field in time:
                            time = str(time).replace(str(field), str(field_value))
                time = time.replace('[', '').replace(']', '').replace("'", '').replace(",", '').split()
                last_time=time[4] + '-' + time[2] + '-' + time[0] + ' ' + time[6] + ':' + time[7] + ':00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.find(attrs={'id': 'category_load_more_container'})
            for i in articles:
                try:
                    article_url = i.a['href']
                    if article_url == "#":
                        continue
                except:
                    continue
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        d_date = {'០': '0', '១': '1', '២': '2', '៣': '3', '៤': '4', '៥': '5', '៦': '6', '៧': '7',
                  '៨': '8', '៩': '9', 'ខែ': 'month', 'ឆ្នាំ': 'year',
                  '២០២២': '2022', 'មករា': '01', 'កុម្ភៈ': '02', 'មីនា': '03', 'មេសា': '04', 'ឧសភា': '05',
                  'មិថុនា': '06', 'កក្កដា': '07',
                  'សីហា': '08', 'កញ្ញា': '09', 'តុលា': '10', 'ិច្ឆិកា': '11', 'ធ្នូ': '12', 'ម៉ោង': '时间'}
        global images, bodys
        soup = BeautifulSoup(response.text, 'html.parser')
        essay_time = soup.time.string
        essay_time = essay_time.replace('<br>', '').replace(':', ' ').split()
        for m in d_date:
            for field in d_date:
                field_value = d_date[field]
                if field in essay_time:
                    essay_time = str(essay_time).replace(str(field), str(field_value))
        essay_time = essay_time.replace('[', '').replace(']', '').replace("'", '').replace(",", '').split()
        t = essay_time[4] + '-' + essay_time[2] + '-' + essay_time[0] + ' ' + essay_time[6] + ':' + essay_time[
            7] + ':00'
        response.meta['title'] = soup.select_one('#article_highlight > div > div.row.article-top > div.article-recap > h1').text
        response.meta['pub_time'] = t
        pages = soup.select('.content-text figure picture')
        for i in pages:
            images_ones = i.select_one('source').get('srcset')
            images = images_ones.replace('780w', '').replace('768w', '').replace('266w', '')
        abstract = str(soup.select('#article_highlight > div > div.row.recap > div.right-recap > div > div > p')).replace('[','').replace(
                       ']', '').replace('<p>', '').replace('</p>', '')
        body_1 = soup.select('div.content-text > p')
        for i in body_1:
            body_2 = i.text
            body = re.sub("[a-zA-Z]", "", body_2)
            bodys = ''.join(body)
        item = NewsItem()
        item['title'] = response.meta['title']
        item['abstract'] = abstract
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['images'] = images
        item['body'] = bodys
        yield item

