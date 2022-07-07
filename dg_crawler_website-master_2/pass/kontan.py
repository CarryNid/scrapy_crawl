# encoding: utf-8
import requests
import scrapy
from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
import re
import common.date as date

# author:凌敏
india_month = {
    'Januari': '01', 'Februari': '02', 'Maret': '03', 'April': '04', 'Mei': '05', 'Juni': '06',
    'Juli': '07', 'Agustus': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Desember': '12'
}


class kontanSpider(BaseSpider):
    name = 'kontan'
    website_id = 51
    language_id = 1952
    start_urls = ['https://insight.kontan.co.id/ajak/loadmore_rubrik/?offset=6&id_rubrik=170']  # http://www.kontan.co.id/
    # is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        li = soup.select('div > ul > li')
        for i in li:
            images = i.find('div', class_='thumb_ls').find('img').get('src')
            content_url = i.find('h2', class_='jdl_lst').find('a').get('href')
            title = i.find('h2', class_='jdl_lst').find('a').text
            ind_time = i.find('div', class_='ls_txt').find('span', class_='gr_ls').text
            year = ind_time.split(' ')[3]
            month = india_month[ind_time.split(' ')[2]]
            day = ind_time.split(' ')[1]
            pub_time = year+'-'+month+'-'+day+' 00:00:00'
            last_time = pub_time
            meta = {'images': images,
                    'title': title,
                    'pub_time': pub_time}
            yield scrapy.Request(url=content_url, callback=self.parse2, meta=meta)
        url = response.url.split('offset=')[0] + 'offset=' + str(int(response.url.split('offset=')[1].split('&')[0]) + 10) + '&id_rubrik=170'
        if self.time is not None:
            if self.time < DateUtil.formate_time2time_stamp(last_time):
                yield scrapy.Request(url, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url, callback=self.parse)

    def parse2(self, response, **kwargs):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['category1'] = soup.find('div', class_='jdl_blue t-uppercase').text
        item['category2'] = ''
        item['body'] = ''
        for i in soup.find('div', class_='ctn').find_all('p'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('.')[0]
        item['title'] = response.meta['title']
        item['images'] = response.meta['images']
        item['pub_time'] = response.meta['pub_time']
        yield item



