# encoding: utf-8

from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from bs4 import BeautifulSoup

#author:吴元栩

class BaodautuSpider(BaseSpider):
    name = 'baodautu'
    website_id = 2051
    language_id = 2242
    types = ["thoi-su-d1/p" ,"dau-tu-d2/p","batdongsan/vat-lieu-cong-nghe-c34/p","batdongsan/kien-truc-phong-thuy-c35/p","batdongsan/chuyen-lang-chuyen-pho-c33/p","batdongsan/du-an--quy-hoach-c32/p","batdongsan/chuyen%20dong-thi-truong-c31/p","quoc-te-d54/p","doanh-nghiep-d3/p","doanh-nhan-d4/p","ngan-hang-d5/p","tai-chinh-chung-khoan-d6/p","suc-khoe-doanh-nghiep-d53/p","diem-nong-d41/p","y-te---suc-khoe-d78/p","tieu-dung-d8/p","o-to-xe-may-d9/p","du-lich-d55/p","vien-thong--cong-nghe-d10/p","dau-tu-phat-trien-ben-vung-d52/p","thong-tin-doanh-nghiep-d36/p"]
    # types = [""]
    start_urls = [f'https://baodautu.vn/{type}{i}' for type in types for i in range(1,2)]
    # start_urls = ["https://baodautu.vn/infographic-quan-he-doi-tac-chien-luoc-viet-nam---vuong-quoc-anh-m154656.html"]
    def parse(self, response):
        hreflist = []
        soup  = BeautifulSoup(response.text , 'html.parser')
        href1 = soup.find(class_="thumbblock thumb555x335 mb20").get("href")
        href2 = soup.find(class_="thumbblock thumb275x155").get("href")
        href3 = soup.find(class_="fs18 fbold").get("href")
        hreflist.append(href1)
        hreflist.append(href2)
        hreflist.append(href3)
        hreflist1 = soup.findAll(class_="title_thumb_square fs16")
        for i in hreflist1:
            # print(i)
            href = i.get("href")
            hreflist.append(href)
        hreflist2 = soup.find_all(class_="fs22 fbold")
        for i in hreflist2 :
            href = i.get("href")
            hreflist.append(href)

        # test_list = ["https://baodautu.vn/infographic-cpi-thang-62022-tang-069-m168701.html","https://baodautu.vn/infographic-cpi-binh-quan-6-thang-nam-2022-tang-244-m168754.html","https://baodautu.vn/infographic-phong-chong-tham-nhung-tieu-cuc-da-ky-luat-hon-170-can-bo-cap-cao-dien-trung-uong-quan-ly-m168904.html","https://baodautu.vn/infographic-6-thang-nam-2022-ca-nuoc-xuat-sieu-710-trieu-usd-m168905.html"]
        # for i in test_list:

        for i in hreflist :
            yield Request(url=i, callback=self.parse_page_content)

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text , 'html.parser')
        item = NewsItem()
        img = []

        judge = soup.find("p").text
        if judge == '.' :
            pic = soup.find("p").find("img").get("src")
            img.append(pic)
            item['images'] = img
            item['title'] = None
            item['category1'] = None
            item['body'] = None
            item['abstract'] = None
            item['pub_time'] = DateUtil.time_now_formate()\

        else:
            # 标题
            title = soup.find(class_="title-detail").text
            item['title'] = title

            #文章类型
            try:
                i=soup.find(class_="fs16 text-uppercase").find("a").text
            except:
                i = soup.find(class_="author cl_green").text
            item['category1'] = i

            # 时间,按年月日时间
            time_ = soup.find(class_="post-time").text
            timelist = time_.split(" ")
            dategeneral = timelist[2]
            datelist = dategeneral.split("/")
            date = "{}-{}-{}".format(datelist[2], datelist[1], datelist[0])
            pub_time = "{}  {}".format(date, timelist[3])
            item['pub_time'] = pub_time

            # 照片
            try:
                i = soup.find(class_="MASTERCMS_TPL_TABLE").find("img").get("src")
            except:
                try:
                    i = soup.select("#content_detail_news > table > tbody > tr > td > img").text#content_detail_news > table > tbody > tr > td > img
                except:
                    i = None
            img.append(i)
            item['images'] = img

            # 文章简介
            sapo_detail = soup.find(class_="sapo_detail").text
            item['abstract'] = sapo_detail

            # 文章内容:照片简介 文章内容
            body = ""
            try:
                i = soup.select_one("#content_detail_news > table > tbody > tr:nth-child(2) > td ").text  # //*[@id="content_detail_news"]/table/tbody/tr[2]/td/text()[1]
            except:
                 i = ""
                 body += i
            bodylist = soup.select("#content_detail_news > p ")  ##content_detail_news > p:nth-child(2)
            for i in bodylist:
                k = i.text
                body += '\n' + k
            item["body"] = body

        print(item["title"])
        print(item['images'])
        yield item