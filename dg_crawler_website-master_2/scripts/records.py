import time
from libs.mysql import Mysql
from config.db_config import *
from libs.excel import Excel
from libs.mail import Mail
import datetime

smtp = 'smtp.163.com'  # smtp域名
sender = 'gdufs_shuwa@163.com'
passwd = 'UZWEIBYLWAOVDQYK'  # 授权码(gdufs_shuwa)
receivers = [  # 收件人邮箱
    'gdufs_shuwa@163.com',
    '657742829@qq.com',
    'jiangshengyi@163.com',
    '1090030606@qq.com',  # 林晓钿
    '331423904@qq.com',
    'chenxuanqi6@163.com',
    '2630862330@qq.com',  # WPF
    '1226144058@qq.com'  # LingMin
    '2754976781@qq.com'
    '467691306@qq.com',  # pys
    '2905939881@qq.com',  # zjx
    '734200940@qq.com',  # 刘鼎谦
]
file = '{}爬虫启动率.xls'
all_info_fields = ["id", "url", "c_name", "remark", "developer", "starting_rate"]


selectHasRunSQL = "SELECT website_id WHERE cole_time like '{}*' "


def get_whole_year(year: int):
    # year(int) : 如2022
    # 获取当前年份中所有日期
    # 返回一个每个元素为"%Y-%m-%d"格式的列表
    begin = datetime.date(year, 1, 1)
    now = begin
    end = datetime.date(year, 12, 31)
    delta = datetime.timedelta(days=1)
    days = []
    while now <= end:
        days.append(now.strftime("%Y-%m-%d"))
        now += delta
    return days


def get15DaysBefore(today: str):
    # today(str) : "%Y-%m-%d"
    # 获取当前时间前15天的事件列表
    # 返回每个日期为 "%Y-%m-%d"格式的列表，15天前~昨天
    this_year = datetime.datetime.now().year
    whole_year_list = get_whole_year(this_year)
    loc = whole_year_list.index(today)
    list = []
    for i in range(loc - 15, loc):
        list.append(whole_year_list[i])
    return list


def getAllActiveWebsiteInfo(common_website_db: Mysql):
    # common_website_db(Mysql) : 通过Mysql构造函数获得,为common_website数据库
    # 获取数据库中所有status=1的网站信息的列表
    # 返回每个元素为[id,url,c_name,remark,developer]的网站列表
    sql = "SELECT id,url,c_name,remark,developer FROM website WHERE status=1"
    origin_all_list = list(common_website_db.select(sql))
    all_list = []
    for elem_tuple in origin_all_list:
        elem_list = list(elem_tuple)
        all_list.append(elem_list)
    # 把元组转化为列表
    return all_list


def get15DaysRecordsInWebList(dg_db: Mysql, web_id_list: list, date: str):
    # dg_db(Mysql): 通过Mysql构造函数获得,为dg_db_website数据库
    # web_id_list(list): int类型的列表, 元素为网页id
    # date(str): 需要获取的前15天的记录的日期，格式为"%Y-%m-%d"
    # 获取对列表中的网页通过爬虫获得文章的15日内日期
    # 返回一个字典.为{web_id1:{[t1,t2,t3...]},web_id2:{t1,t2,t3...}}
    before_15days = get15DaysBefore(date)
    all_web_records = {}
    for web_id in web_id_list:
        sql = "SELECT cole_time FROM news WHERE cole_time >='{}' AND cole_time<='{}' AND website_id={} "
        result_list = []
        sql_f = sql.format(before_15days[0], before_15days[-1], web_id)
        one_web_records = dg_db.select(sql_f)  # ((time1,)(time2,)...)  查找单个网站在过去15天内的文章爬取日期记录
        for one_record in one_web_records:
            cole_time = one_record[0].strftime("%Y-%m-%d")
            if cole_time not in result_list:  # 去重
                result_list.append(cole_time)
        all_web_records[web_id] = result_list
    return all_web_records


def run():
    common_db = Mysql(COMMON_WEBSITE_CONFIG)
    dg_db = Mysql(WEBSITE_CONFIG_LIST['01'])
    all_info = getAllActiveWebsiteInfo(common_db)
    web_id_list = []
    for info in all_info:
        web_id_list.append(info[0])
    print("web_id_list", web_id_list)
    all_info.insert(0, all_info_fields)
    print(all_info)
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    all_web_records = get15DaysRecordsInWebList(dg_db, web_id_list, today)
    for i in range(1, len(all_info)):
        web_id = web_id_list[i-1]
        starting_rate = str((len(all_web_records[web_id])*100)/15.0)[0:5]+"%"
        all_info[i].append(starting_rate)
        print(web_id, ": ", starting_rate)

    time_section = get15DaysBefore(today)
    time_section_str = time_section[0]+"-"+time_section[-1]
    file_ = file.format(time_section_str)
    book = Excel(file_)
    book.add_sheet("活跃中", all_info)
    book.save()
    subject = '{}期间status=1的爬虫启动率'.format(time_section_str)
    message = Mail(sender=sender, receivers=receivers, passwd=passwd, smtp=smtp, subject=subject)
    message.attach_file(file_)
    message.send()
    # all_info为需要发送的邮件中的data，需补充发送


# python -m scripts.records
if __name__ == '__main__':
    run()