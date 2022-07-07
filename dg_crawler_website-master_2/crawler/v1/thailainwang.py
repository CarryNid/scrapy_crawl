from crawler.spiders import BaseSpider
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

days = {
        '天前': 'days ago',
        '前天': '2 days ago',
        '昨天': '1 days ago',
        '小时前': 'hours ago',
}

# author 武洪艳
class ThailainwangSpider(BaseSpider):
    name = 'thailainwang'
    # allowed_domains = ['www.thailianwang.com/portal.php?mod=list']
    start_urls = ['http://www.thailianwang.com/portal.php?mod=list/']  # http://www.thailianwang.com/portal.php?mod=list&catid=2
    website_id = 1604  # 网站的id(必填)
    language_id = 1813  # 语言
    is_http = 1
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'root',
    #     'password': 'why520',
    #     'db': 'dg_crawler'
    # }
    # 这是类初始化函数，用来传时间戳参数


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#hd > div > div.rtj1009_nav3 > div.z.ren_navyi.cl > ul > li a')
        for category in categories:
            if category.get('href') == 'forum.php?mod=forumdisplay&fid=2&filter=typeid&typeid=2':
                category_url = 'http://www.thailianwang.com/' + category.get('href')
            else:
                category_url = 'http://www.thailianwang.com' + category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        last_time = soup.select('div.z.ren_tie_xz > div.z.ren_tie_zhhf > div.z.ren_list_tiezz > span:nth-child(3)')[-1].text + ' 00:00:00'
        if self.time is None or Util.format_time3(last_time) >= int(self.time):
            articles = soup.select('#threadlisttableid > tbody a.s.xst')
            for article in articles:
                article_url = 'http://www.thailianwang.com/' + article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = 'http://www.thailianwang.com/' + soup.select_one('#fd_page_top\ y > div > a.nxt').get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#thread_subject').text
        t = soup.select_one('.ren_view_authisj').text.split(' ')
        if len(t) == 2:
            tt = t[1].split('\xa0')
            if tt[0] == '昨天' or tt[0] == '前天':
                item['pub_time'] = Util.format_time2(days[tt[0]])
            if tt[1] == '天前' or tt[1] == '小时前':
                item['pub_time'] = Util.format_time2(tt[0] + ' ' + days[tt[1]])
        else:
            item['pub_time'] = t[1] + ' ' + t[2]
        item['images'] = ['http://www.thailianwang.com/' + img.get('file') for img in soup.select('.t_f img') if img.get('file') != None]
        p_list = []
        if soup.select('.t_f'):
            for paragraph in soup.select('.t_f'):
                if paragraph.text.strip() != ' ' and paragraph.text.strip() != '\n':
                    p_list.append(paragraph.text.strip())
            body = '\n'.join(p_list)
            item['body'] = body
        if p_list[0] != '':
            item['abstract'] = p_list[0]
        else:
            if p_list[1] != '':
                item['abstract'] = p_list[1]
            else:
                if p_list[2] != '':
                    item['abstract'] = p_list[2]
                else:
                    if p_list[3] != '':
                        item['abstract'] = p_list[3]
        return item